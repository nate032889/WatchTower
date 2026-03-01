## AI Assistant Guidelines

Before making decisions or changes, please reference this document. To provide new guidelines, such as for the `agents` library, create a corresponding markdown file (e.g., `guidelines/AGENTS.md`) and I will incorporate it.

# Architectural Guidelines & Preferences

> *"Life is really simple, but we insist on making it complicated."* — Confucius
> *"Any intelligent fool can make things bigger, more complex, and more violent. It takes a touch of genius and a lot of courage to move in the opposite direction."* — Albert Einstein
> *"All problems in computer science can be solved by another level of indirection. But that usually will create another problem."* — David Wheeler
> *"The architecture should be independent of frameworks!"* — Bob Martin

This document outlines the core architectural principles, design patterns, and tactical execution standards required for this codebase. The ultimate goal of these guidelines is to maximize readability, enforce strict boundaries, and embrace simplicity.

**Remember:**
* System design is about tradeoffs.
* Don't refactor just for the sake of refactoring. All code is trash.
* Senior Engineers don't add code, they **REMOVE** code.

---

## 1. System Architecture & Microservices

* **The Microservice Reality:** Performance is *not* the main focus of microservices. Single-request performance in a distributed system is inherently slower due to network overhead. We use microservices for independent scalability, rigorous enforcement of decoupled boundaries, and simplified release processes. Keep workers isolated to maximize this independence.
* **Domain-Driven Design (DDD):** Core business logic must be isolated from delivery mechanisms and infrastructure. Interfaces, Views, and API layers contain *zero* business logic. Infrastructure (APIs, LLMs, DBs) must be treated purely as external data planes abstracted behind interfaces.
* **Indirection vs. Abstraction:** Use abstraction to hide complexity and reveal intent. Use indirection carefully to decouple systems. Be mindful of Wheeler's law: every layer of indirection solves one problem but introduces another (usually cognitive load or latency).

## 2. Cohesion, Coupling, and State

* **Maximize Cohesion, Minimize Coupling:** Group highly related things together. A class should not depend directly on another class; both should depend on an abstraction. Depending on an interface is loose coupling, but use it with caution—do not build interfaces for things that only have a single implementation.
* **Reduce State & State Mutation:** Start with methods; let state fall in after. Be minimalist and practice YAGNI (You Aren't Gonna Need It). Messing with state is the root of many problems. Mutability needs company; it often hangs around with bugs.
* **Favor Composition Over Inheritance:** Inheritance is vastly overused and demands more from a developer. It should *only* be used for pure substitutability (The Liskov Substitution Principle). If an object of B should use an object of A, use composition/delegation.
* **Dependency Inversion:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

## 3. Tactical Code Execution

* **Single Level of Abstraction Principle (SLAP) & Compose Method:** All functions must be composed at the *same* level of detail. Do not mix high-level orchestration with low-level string manipulation.
* **Method Size & Nesting:** Long methods are hard to test, read, debug, and reuse. They obscure business rules. The size of a function is acceptable when it fits within a single screen, but the true metric of complexity is the length of nesting. Extract and invert conditionals to keep the primary path clear.
* **Tell, Don't Ask:** Instead of asking an object for its data and acting upon it, tell the object what to do. Push behavior down into the objects that hold the data.
* **Avoid Primitive Obsession (Accidental Complexity):** Do not use basic data types (strings, integers, arrays) to represent domain concepts. Use functional built-ins that are idiomatic to the language to handle data transformations.
* **Knock Out Before You Mock Out:** Deal with and isolate your actual dependencies as much as possible before resorting to heavy mocking in your testing strategy.

## 4. Readability & Intent

* **The Golden Rule of Readability:** The quality of code is inversely proportional to the effort it takes to understand it.
* **Naming is Understanding:** If you cannot name a variable or a function appropriately, it is a sign you have not yet understood its true purpose. Good, meaningful names eliminate the need for explanations.
* **Comment the 'Why', Not the 'What':** Good code is self-documenting. It already explains *how* it works and *what* it is doing. Comments must be reserved strictly for providing the greater context surrounding the code.
* **Avoid Clever Code:** It takes a genius to create something simple. Do not write "clever" one-liners that obscure the execution flow.

## 5. Engineering Culture & Code Reviews

* **Peer Reviews Complement Testing:** Active peer reviews catch 60% of defects. Perspective-based reviews (reviewing from the lens of security, performance, or a specific user) catch 35% more defects than non-directed reviews.
* **Constructive Feedback:** Never just say what's wrong; always say what's better. Code review is a social activity as much as a technical one.
* **Tactical Reviewing:** Review the test *before* reviewing the code. If the tests do not make sense, the implementation does not matter. Write the test *while* fixing the bug.

## 6. Framework Specifics (Python/Django & Go)

* **Paradigm Splitting:** * **Declarative/Functional:** Tell the system *what* NOT *how*. Excellent for scale, parallelization, and reasoning. Prefer this in core Service Layers.
    * **Imperative/OOP:** Tell the system *what* AND *how*. Good for side-effects and exceptions. Use strictly for Views, Serialization, Repositories, and external clients.
* **View Layer Strictness:** No business logic lives in a View. Views parse data, pass it to a Service, and return a response.
* **Go-Style Error Handling (Python):** Avoid deep `try/except` blocks. Use Error Objects or tuple returns to encapsulate exceptions (e.g., `data, err = do_something()`).
