# 思考接口探测

[运行记录](https://github.com/fastisrealslow/li-lu-13f/actions/runs/35215503163)

Qwen3.5 9B Q8_0、Ollama 0.34.1，在原生 JSON schema 约束下启用 think=true。6/6 请求最终 response 为空，JSON 内容出现在 thinking 字段，均以 stop 正常结束，无截断或超时。该轮属于接口兼容性探测，不能用来评价思考后的事实准确率，也未从 thinking 取 JSON 冒充最终答案。

后续把相同 schema 放入提示词，同时对开、关思考两组去掉原生 format，最终答案仍经严格 JSON 校验。
