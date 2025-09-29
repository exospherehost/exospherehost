@@
      class DataProcessorNode(BaseNode):
          class Inputs(BaseModel):
              data: str
              operation: str
@@
          async def execute(self) -> Outputs:
              # Parse the input data
              try:
                  data = json.loads(self.inputs.data)
-             except:
-                 return self.Outputs(
-                     result="",
-                     status="error: invalid json"
-                 )
+             except json.JSONDecodeError as e:
+                 # Invalid JSON input; return a helpful, specific error
+                 return self.Outputs(
+                     result="",
+                     status=f"error: invalid json (line {e.lineno}, column {e.colno})"
+                 )
              # Process based on operation
              if self.inputs.operation == "transform":
                  result = {"transformed": data, "processed": True}
              else:
                  result = {"original": data, "processed": False}
