# Trailer content evidence

Source inspection on 2026-11-11. This brief supplies technical substance for the approved motion-led scenario. Each visual translates an implemented relationship into abstract motion, with a brief genuine capture where it helps establish the connection to working software.

## Revision basis

| Repository            | Inspected HEAD                             |
| --------------------- | ------------------------------------------ |
| Core                  | `a9b1324a32e4093ebbeaad81fea9994136e528d5` |
| Applications          | `0f89bbfe1b2388173475881fb941fbd7bfe4cabb` |
| Platforms             | `e6ee588744e3c968696b74ead6d19f02f9d68dc6` |
| Website documentation | `f3517f247ec52896e8a6bf508631a2e65ea0a590` |

These are source references for editorial development. Existing captures have their own older host/guest pins in production capture manifests. A future capture must record the dependencies actually built and the guest bundle actually loaded. New local source checkouts alone do not update a runtime's Cargo lockfile or installed guest bundles.

## 1. Execution with a visible cause and effect

**Supported argument** — Xila runs WebAssembly applications through its Wasmi-based runtime. Execution uses a fuel budget per cooperative slice. Resumption replenishes fuel, including the amount needed for a larger operation.

**Visual proposal for 00:28–00:40** — A moving module crosses into a bounded runtime structure. An advancing signal pauses at deliberate boundaries and resumes. Follow one signal into a real application action, then return to abstract motion. The pauses and routes are editorial representations; the animation's speed and packet count carry no measured performance meaning.

**Copy** — Keep `WebAssembly applications.` The implemented fuel mechanism can shape the animation without adding another explanatory headline.

**Evidence** — [Execution and fuel replenishment](https://github.com/xila-project/applications/blob/0f89bbfe1b2388173475881fb941fbd7bfe4cabb/executables/wasm/src/host/execution.rs), [runtime setup](https://github.com/xila-project/applications/blob/0f89bbfe1b2388173475881fb941fbd7bfe4cabb/executables/wasm/src/host/main.rs), [runtime documentation and limitations](https://github.com/xila-project/applications/blob/0f89bbfe1b2388173475881fb941fbd7bfe4cabb/executables/wasm/README.md).

**Verification status** — Source inspected. This session did not execute scheduling or performance tests. Graphics bindings have a supported-call subset and a revision-dependent ABI. Claims about universal Wasm compatibility, hard real-time guarantees or complete isolation would require additional evidence.

## 2. An actual application round trip

**Supported argument** — Pixel Painter consumes pointer events with coordinates and updates an indexed canvas through Xila's guest graphics bridge. Its runtime documentation describes validation and copying of palette and pixel data into host-owned image storage.

**Visual proposal for 00:40–00:49** — Match an abstract moving signal to a real pointer stroke. The stroke grows inside the genuine application. Match its final direction back to the geometric route. This provides one continuous action across the conceptual and recorded parts of the film.

**Copy** — The application action supplies the evidence without additional copy.

**Evidence** — [Pointer input and canvas updates](https://github.com/xila-project/applications/blob/0f89bbfe1b2388173475881fb941fbd7bfe4cabb/executables/pixel_painter/src/interface.rs), [graphics architecture and bounds](https://github.com/xila-project/applications/blob/0f89bbfe1b2388173475881fb941fbd7bfe4cabb/executables/wasm/README.md#graphics-architecture).

**Verification status** — The earlier native session successfully launched Pixel Painter and drew the three stepped paths used in review 002. That observation is pinned in `productions/architecture-reveal/capture.json`. Current source inspection supplies an updated editorial reference. The scenario still needs an actual motion recording of the chosen action.

## 3. A shared namespace across different resources

**Supported argument** — Xila's VFS routes path operations to mounted backends and applies task/user context and access policy. Files, devices and pipes share a namespace; each backend supplies its own behavior.

**Visual proposal for 01:01–01:13** — Three different resource forms join a common route. A single request follows that route to its selected endpoint. Distinct endpoint responses make the relationship legible while keeping the composition abstract. This gives the coherent-system passage a concrete subject beyond another generic activation montage.

**Possible small diagram labels** — `Files`, `Devices`, `Pipes`. These appear as supporting labels in scenario draft 2 and need a rendered composition review.

**Evidence** — [VFS explanation and request flow](https://github.com/xila-project/website/blob/f3517f247ec52896e8a6bf508631a2e65ea0a590/src/content/docs/explanation/architecture/subsystems/virtual_file_system.mdx), [file operations](https://github.com/xila-project/core/blob/a9b1324a32e4093ebbeaad81fea9994136e528d5/subsystems/virtual_file_system/src/file.rs), [synchronous file API](https://github.com/xila-project/core/blob/a9b1324a32e4093ebbeaad81fea9994136e528d5/subsystems/virtual_file_system/src/synchronous_file.rs).

**Verification status** — Documentation and file API inspected. No new VFS acceptance tests were run in this session. Any recorded demonstration should exercise the selected operation on the actual runtime.

## 4. Additional demonstrations available for later selection

| Candidate            | What the sources support                                                                                                    | Possible use                                   | Verification needed before footage                                                                                                                         |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Digits               | A Wasm guest writes a prepared digit tensor to `/devices/nn/digits`, requests computation and reads predictions             | A short input → device → response illustration | Run the selected drawing on the intended native host and retain its real result. Freehand accuracy and embedded-hardware execution remain unverified here. |
| Package installation | The native `package` CLI verifies publisher signatures and payload hashes, then publishes a verified bundle from quarantine | A package moving through verification stages   | Run a controlled signed-package installation with the required root task. Account for the documented lifecycle limits before selecting this subject.       |

Sources include [Digits](https://github.com/xila-project/applications/blob/0f89bbfe1b2388173475881fb941fbd7bfe4cabb/executables/digits/README.md) and [package installation](https://github.com/xila-project/applications/blob/0f89bbfe1b2388173475881fb941fbd7bfe4cabb/executables/package/README.md). Digits documents model limitations and distinguishes native/browser demonstrations from hardware validation. The package CLI documents privilege requirements, trust handling and lifecycle features that remain future work.

## Editorial selection

Develop the next WebAssembly passage around execution, the graphics bridge and a real application round trip. Use the shared-resource namespace to give the later coherent-system sequence a distinct visual purpose. Keep Digits and package installation as candidates until their capture workloads are verified and their relevance to the edit is reviewed.

The current headline set is maintained in SCENARIO.md as an editorial draft. This evidence brief adds source-backed subjects and capture requirements; its proposed diagrams and supporting labels still need a rendered creative review.
