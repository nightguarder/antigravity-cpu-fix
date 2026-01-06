#!/usr/bin/env python3
import hashlib
import os
import sys

if len(sys.argv) < 2:
    print("❌ Error: Missing Argument. Usage: revert_patch.py <AG_DIR>")
    sys.exit(1)

base_dir = sys.argv[1]
target_files = ["resources/app/out/jetskiAgent/main.js"]

# The exact polyfill string used in patch_code.py
polyfill = b"""{
  const _f = globalThis.fetch;
  if (_f) {
    globalThis.fetch = (u, o) => {
      if (typeof u === "string" && u.includes("antigravity")) {
        return Promise.reject(new TypeError("Blocked by Antigravity Patch"));
      }
      return _f(u, o);
    };
  }
  const _si = globalThis.setInterval;
  globalThis.setInterval = (fn, ms, ...args) => {
    if (typeof ms === 'number' && ms < 1000) ms = 1200;
    return _si(fn, ms, ...args);
  };
  globalThis.queueMicrotask = (fn) => setTimeout(fn, 1200);
  globalThis.requestAnimationFrame = (fn) => setTimeout(fn, 1200);
}
const __slowMo = (fn) => setTimeout(fn, 1200);
"""

for rel_path in target_files:
    file_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(file_path):
        print(f"⚠️  Skipping: {rel_path} (Not found)")
        continue

    with open(file_path, "rb") as f:
        content = f.read()

    original_hash = hashlib.md5(content).hexdigest()

    if b"Blocked by Antigravity Patch" in content:
        # Try exact replacement first
        exact_patch_str = polyfill + b"\n"
        
        if content.startswith(exact_patch_str):
             new_content = content[len(exact_patch_str):]
        else:
            # Fallback: simple replace if it's not at the start or format differs slightly
            # ignoring newline differences for safer removal
            new_content = content.replace(exact_patch_str, b"")
            if new_content == content:
                 new_content = content.replace(polyfill, b"")

        if new_content != content:
            new_hash = hashlib.md5(new_content).hexdigest()
            try:
                with open(file_path, "wb") as f:
                    f.write(new_content)
                print(f"✅ Reverted: {rel_path}")
                print(f"  New Hash: {new_hash}")
            except Exception as e:
                print(f"❌ Error writing {rel_path}: {e}")
        else:
             print(f"⚠️  Could not cleanly remove patch from: {rel_path} (Content mismatch)")
             
    else:
        print(f"ℹ️  Not Patched: {rel_path} (Clean)")
