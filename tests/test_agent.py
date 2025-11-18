import unittest
from src.agent import ReactAgent

class TestAgent(unittest.TestCase):

    def test_parse_llm_response(self):
        agent = ReactAgent(task="test", repo=".", max_iterations=1, llm_client=None)
        xml_response = """
<response>
  <thought>This is a thought.</thought>
  <action>
    <tool_name>my_tool</tool_name>
    <parameters>
      <param1>value1</param1>
      <param2>value2</param2>
    </parameters>
  </action>
</response>
"""
        thought, tool_name, params = agent._parse_llm_response(xml_response)

        self.assertEqual(thought, "This is a thought.")
        self.assertEqual(tool_name, "my_tool")
        self.assertEqual(params, {"param1": "value1", "param2": "value2"})

if __name__ == '__main__':
    unittest.main()
