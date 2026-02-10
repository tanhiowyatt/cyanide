import pickle
from cyanide.core.filesystem_nodes import Directory, File

import hmac
import hashlib

# from cyanide.core.security import loads as safe_loads # Removed in favor of local SafeUnpickler
import builtins
import io

class SafeUnpickler(pickle.Unpickler):
    """
    Secure Unpickler that restricts deserialization to a strict whitelist.
    """
    # Allowed primitive types from builtins
    SAFE_BUILTINS = {
        'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'range', 'slice', 
        'NoneType', 'bytes', 'complex'
    }
    
    # Allowed internal classes (if they were to be pickled directly)
    # Based on current to_dict implementation, these might not be strictly needed for fs_dict,
    # but are included as per requirements for filesystem snapshot consistency.
    SAFE_CLASSES = {
        'cyanide.core.filesystem_nodes': {'File', 'Directory', 'Node', 'DynamicFile'},
        # Handle cases where module might be referenced differently
        'src.cyanide.core.filesystem_nodes': {'File', 'Directory', 'Node', 'DynamicFile'}
    }

    def find_class(self, module, name):
        # 1. Allow Safe Builtins
        if module == "builtins":
            if name in self.SAFE_BUILTINS:
                return getattr(builtins, name)
            # Reject unsafe builtins (eval, exec, etc.)
        
        # 2. Allow Specific Internal Classes
        if module in self.SAFE_CLASSES:
            if name in self.SAFE_CLASSES[module]:
                return super().find_class(module, name)
                
        # 3. Reject Everything Else
        raise pickle.UnpicklingError(f"SafeUnpickler: Forbidden class '{module}.{name}'")

# Internal Integrity Key
# This prevents loading arbitrary pickle files not created by this tool.
# It is NOT a cryptographic secret for external security, but an integrity check.
INTEGRITY_KEY = b"cyanide-honeypot-internal-integrity-key-v1"

def save_fs(root_node, path: str):
    """Save filesystem to signed pickle file."""
    # Serialize to dict first
    fs_dict = root_node.to_dict()
    
    # Dump to bytes
    # nosemgrep: python.lang.security.deserialization.pickle.avoid-pickle
    data = pickle.dumps(fs_dict)
    
    # Calculate HMAC
    signature = hmac.new(INTEGRITY_KEY, data, hashlib.sha256).digest()
    
    with open(path, "wb") as f:
        # Format: [32 bytes HMAC][Pickle Data]
        f.write(signature)
        f.write(data)

def load_fs(path: str):
    """Load filesystem from signed pickle file."""
    with open(path, "rb") as f:
        # Read HMAC
        signature = f.read(32)
        data = f.read()
        
    # Verify HMAC
    expected = hmac.new(INTEGRITY_KEY, data, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        print(f"Error: Filesystem integrity check failed for {path}")
        return None
        
    # Use safe unpickler on trusted data
    try:
        # fs_dict = safe_loads(data)
        # Use SafeUnpickler
        fs_dict = SafeUnpickler(io.BytesIO(data)).load()
    except Exception as e:
        print(f"Error unpickling FS: {e}")
        return None
            
    # Reconstruct objects
    if fs_dict.get("type") == "dir":
        return Directory.from_dict(fs_dict)
    elif fs_dict.get("type") == "file":
        return File.from_dict(fs_dict)
    return None
