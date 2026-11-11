# Capture the native Xila interface

Use the Debug application shipped by Platforms to capture the composited Xila screen. The native headless driver supports this workflow without a desktop display server. The client must run as the same host user as the runtime. Follow the checked-out Platforms README and AGENTS.md for its current protocol.

Before capturing, compare the actual Core and Applications revisions in Platforms’ Cargo lockfile with the UI revision you intend to show. A new local Applications checkout does not change the runtime’s locked dependencies. Record the guest bundle version separately.

From `../workspace/repositories/platforms`, build the runtime and client with its existing lockfile. Run Cargo from that directory so its native configuration is loaded. A clean archive of a committed Platforms revision can provide an isolated capture build when the working tree contains other work.

```sh
cargo build --locked -p xila-native-example -p xila-drivers-native \
  --bin native_example --bin xila-debug
mise run image:native
```

Choose a new disk path for each recording session. Keep it under Media's ignored `output/capture/` directory. An existing disk retains its accounts, files and installed applications.

```sh
target/debug/native_example --gui --no-network --display-driver headless \
  --resolution 1280x800 \
  --disk-path /ABSOLUTE/MEDIA/output/capture/SESSION/drive.img \
  --seed-image target/seed/native/seed.img
```

In another terminal in Platforms, discover the capabilities, enter the public default account on a new installation, and capture the screen.

```sh
target/debug/xila-debug capabilities
target/debug/xila-debug click --role textbox --name 'User name'
target/debug/xila-debug text administrator
target/debug/xila-debug wait-for --role textbox --name 'User name' \
  --text administrator --timeout-ms 3000
target/debug/xila-debug click --role button --name Login
target/debug/xila-debug screenshot /tmp/xila-capture.png
```

Inspect the actual PNG and `ui-tree` before selecting the next control. A queued response reports input submission. A successful `wait-for` observes the requested widget state. A timeout with a truncated tree leaves the observation inconclusive. The product study encountered that case after opening multiple windows and verified the screen visually.

If a very brief click is missed by the runtime, use the documented pointer operations with a short held press, then inspect the result.

```sh
target/debug/xila-debug pointer move X Y
target/debug/xila-debug pointer button press
# Release after a short held press.
target/debug/xila-debug pointer button release
```

The task switcher uses an upward gesture from the bottom bar. Resolve current controls through the debug selectors when possible. Coordinates depend on the current resolution and layout. Stop your capture runtime when finished.

Import the final screenshot from Media with `scripts/screens.py`. Record the Platforms revision, relevant local changes, Cargo lock hash, seeded bundle versions, resolution and capture date alongside the production. Raw screenshots retain the displayed content's licensing and attribution. The current captures record Xila's Apache-2.0 and the UI fonts' OFL-1.1 licensing.
