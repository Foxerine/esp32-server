import uuid
import re
from typing import List, Dict
from datetime import datetime


class Message:
    def __init__(
            self,
            role: str,
            content: str = None,
            uniq_id: str = None,
            tool_calls=None,
            tool_call_id=None,
    ):
        self.uniq_id = uniq_id if uniq_id is not None else str(uuid.uuid4())
        self.role = role
        self.content = content
        self.tool_calls = tool_calls
        self.tool_call_id = tool_call_id

    def __str__(self):
        """
        Message 对象的字符串表示，用于调试和日志。
        """
        parts = [f"ID: {self.uniq_id}", f"Role: {self.role}"]
        if self.content:
            # 限制内容长度以避免日志过长
            display_content = self.content
            if len(display_content) > 100:
                display_content = display_content[:97] + "..."
            parts.append(f"Content: '{display_content}'")
        if self.tool_calls:
            # 简化 tool_calls 的显示
            tool_names = [tc.get('function', {}).get('name', 'unknown') for tc in self.tool_calls]
            parts.append(f"Tool Calls: {tool_names}")
        if self.tool_call_id:
            parts.append(f"Tool Call ID: {self.tool_call_id}")
        return f"Message({', '.join(parts)})"

    def __repr__(self):
        """
        Message 对象的官方字符串表示，便于重构。
        """
        return (
            f"Message(role='{self.role}', content='{self.content}', "
            f"uniq_id='{self.uniq_id}', tool_calls={self.tool_calls}, "
            f"tool_call_id='{self.tool_call_id}')"
        )


class Dialogue:
    def __init__(self):
        self.dialogue: List[Message] = []
        # 获取当前时间
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        """
        提供 Dialogue 对象的友好字符串表示，方便在日志中打印对话内容。
        """
        dialogue_str_parts = [f"--- Dialogue (Created: {self.current_time}) ---"]
        if not self.dialogue:
            dialogue_str_parts.append("No messages in this dialogue.")
        else:
            for i, message in enumerate(self.dialogue):
                # 使用 Message 自己的 __str__ 方法来格式化每个消息
                dialogue_str_parts.append(f"[{i+1}] {message}")
        dialogue_str_parts.append("------------------------------------")
        return "\n".join(dialogue_str_parts)

    def put(self, message: Message):
        self.dialogue.append(message)

    def getMessages(self, m, dialogue):
        if m.tool_calls is not None:
            dialogue.append({"role": m.role, "tool_calls": m.tool_calls})
        elif m.role == "tool":
            dialogue.append(
                {
                    "role": m.role,
                    "tool_call_id": (
                        str(uuid.uuid4()) if m.tool_call_id is None else m.tool_call_id
                    ),
                    "content": m.content,
                }
            )
        else:
            dialogue.append({"role": m.role, "content": m.content})

    def get_llm_dialogue(self) -> List[Dict[str, str]]:
        # 直接调用get_llm_dialogue_with_memory，传入None作为memory_str
        # 这样确保说话人功能在所有调用路径下都生效
        return self.get_llm_dialogue_with_memory(None, None)

    def update_system_message(self, new_content: str):
        """更新或添加系统消息"""
        # 查找第一个系统消息
        system_msg = next((msg for msg in self.dialogue if msg.role == "system"), None)
        if system_msg:
            system_msg.content = new_content
        else:
            self.put(Message(role="system", content=new_content))

    def get_llm_dialogue_with_memory(
            self, memory_str: str = None, voiceprint_config: dict = None
    ) -> List[Dict[str, str]]:
        # 构建对话
        dialogue = []

        # 添加系统提示和记忆
        system_message = next(
            (msg for msg in self.dialogue if msg.role == "system"), None
        )

        if system_message:
            # 基础系统提示
            enhanced_system_prompt = system_message.content
            # 替换时间占位符
            enhanced_system_prompt = enhanced_system_prompt.replace(
                "{{current_time}}", datetime.now().strftime("%H:%M")
            )

            # 添加说话人个性化描述
            try:
                speakers = voiceprint_config.get("speakers", []) if voiceprint_config else []
                if speakers:
                    enhanced_system_prompt += "\n\n<speakers_info>"
                    for speaker_str in speakers:
                        try:
                            parts = speaker_str.split(",", 2)
                            if len(parts) >= 2:
                                name = parts[1].strip()
                                # 如果描述为空，则为""
                                description = (
                                    parts[2].strip() if len(parts) >= 3 else ""
                                )
                                enhanced_system_prompt += f"\n- {name}：{description}"
                        except Exception:
                            pass # 忽略单个speaker_str解析错误
                    enhanced_system_prompt += "\n\n</speakers_info>"
            except Exception:
                # 配置读取失败时忽略错误，不影响其他功能
                pass

            # 使用正则表达式匹配 <memory> 标签，不管中间有什么内容
            if memory_str is not None:
                enhanced_system_prompt = re.sub(
                    r"<memory>.*?</memory>",
                    f"<memory>\n{memory_str}\n</memory>",
                    enhanced_system_prompt,
                    flags=re.DOTALL,
                )
            dialogue.append({"role": "system", "content": enhanced_system_prompt})

        # 添加用户和助手的对话
        for m in self.dialogue:
            if m.role != "system":  # 跳过原始的系统消息
                self.getMessages(m, dialogue)

        return dialogue
