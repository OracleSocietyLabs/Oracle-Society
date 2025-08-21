
# Godot Integration Notes
- For in-process mode: port the simple adapters to GDScript/C# (area bumps, rumors, DSL rule parsing).
- For server mode: use `HTTPRequest` for REST and a `Thread` to read `/events/stream` lines and emit signals.
