api_key = "sk-78944c3f22b84cbea80eae4c70bf53c3"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model = "qwen-plus"


def chat(prompt, code_log, enable_debug = False):
    from openai import OpenAI
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=api_key,
        # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url=base_url,
    )
    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model=model,  # qwen-plus 属于 qwen3 模型，如需开启思考模式，请参见：https://help.aliyun.com/zh/model-studio/deep-thinking
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f'代码信息如下（使用git命令获取的代码变更记录），现在请你分析和回答：\n{code_log}'}
        ]
    )

    result = completion.choices[0].message.content
    return result


def general_chat(prompt, user_content, waiting_msg: str = None, enable_debug = False):
    from openai import OpenAI
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=api_key,
        # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url=base_url,
    )
    if enable_debug:
        print("\n" * 3)
        print("=" * 80)
        print(f"\n系统提示：\n\t{prompt}\n")
        print(f"用户输入：\n{user_content}\n")
        print("=" * 80)
        print("\n" * 3)

    if waiting_msg:
        print(waiting_msg)

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model=model,  # qwen-plus 属于 qwen3 模型，如需开启思考模式，请参见：https://help.aliyun.com/zh/model-studio/deep-thinking
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': user_content}
        ]
    )

    result = completion.choices[0].message.content
    return result


def stream_chat(prompt, code_log):
    from openai import OpenAI
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=api_key,
        # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url=base_url,
    )
    completion = client.chat.completions.create(
        model=model,  # qwen-plus 属于 qwen3 模型，如需开启思考模式，请参见：https://help.aliyun.com/zh/model-studio/deep-thinking
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f'代码信息如下（使用git命令获取的代码变更记录），现在请你分析和回答：\n{code_log}'}
        ],
        stream=True,
        # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
        # 使用Qwen3开源版模型时，请将下行取消注释，否则会报错
        # extra_body={"enable_thinking": False},
    )

    full_content = ""
    print("\n流式输出内容为：")
    for chunk in completion:
        # 如果stream_options.include_usage为True，则最后一个chunk的choices字段为空列表，需要跳过（可以通过chunk.usage获取 Token 使用量）
        if chunk.choices:
            full_content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content)
    print(f"完整内容为：\n")
    ctx_arr = full_content.split('\n')
    # 提取第一行
    print(ctx_arr[0])
    # 获取除第一行外的其他行
    print('\n'.join(ctx_arr[1:]))
