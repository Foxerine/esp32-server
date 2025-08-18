<template>
  <div class="welcome">
    <HeaderBar />

    <div class="operation-bar">
      <h2 class="page-title">角色配置</h2>
    </div>

    <div class="main-wrapper">
      <div class="content-panel">
        <div class="content-area">
          <el-card class="config-card" shadow="never">
            <div class="config-header">
              <div class="header-icon">
                <img loading="lazy" src="@/assets/home/setting-user.png" alt="">
              </div>
              <span class="header-title">{{ form.agentName }}</span>
              <div class="header-actions">
                <div class="hint-text">
                  <img loading="lazy" src="@/assets/home/info.png" alt="">
                  <span>保存配置后，需要重启设备，新的配置才会生效。</span>
                </div>
                <el-button type="primary" class="save-btn" @click="saveConfig">保存配置</el-button>
                <el-button class="reset-btn" @click="resetConfig">重置</el-button>
                <button class="custom-close-btn" @click="goToHome">
                  ×
                </button>
              </div>
            </div>
            <div class="divider"></div>

            <el-form ref="form" :model="form" label-width="72px">
              <div class="form-content">
                <div class="form-grid">
                  <div class="form-column">
                    <el-form-item label="助手昵称：">
                      <el-input v-model="form.agentName" class="form-input" maxlength="10" />
                    </el-form-item>
                    <el-form-item label="角色模版：">
                      <div class="template-container">
                        <div v-for="(template, index) in templates" :key="`template-${index}`" class="template-item"
                          :class="{ 'template-loading': loadingTemplate }" @click="selectTemplate(template)">
                          {{ template.agentName }}
                        </div>
                      </div>
                    </el-form-item>
                    <el-form-item label="角色介绍：">
                      <el-input type="textarea" rows="9" resize="none" placeholder="请输入角色的详细背景、性格和特点" v-model="form.systemPrompt"
                                maxlength="2000" show-word-limit class="form-textarea" />
                    </el-form-item>
                    <el-form-item label="回答风格：">
                      <el-input type="textarea" rows="6" resize="none" placeholder="你应该以简短，口语化的方式回答用户的问题，绝对不可以使用任何Markdown格式" v-model="form.reply_style"
                                maxlength="2000" show-word-limit class="form-textarea" />
                    </el-form-item>
                    <!-- ============== 重构后的用法说明部分（中文版） ============== -->
                    <el-form-item label=" ">
                      <div style="display: flex; gap: 10px; text-align: left;">
                        <el-button type="primary" size="small" @click="showUsageInfo = true">
                          查看用法说明
                        </el-button>
                        <el-button type="success" size="small" @click="showRenderPreview = true">
                          查看渲染效果
                        </el-button>
                      </div>

                      <!-- 用法说明弹窗 -->
                      <el-dialog
                          title="模板渲染用法说明"
                          :visible.sync="showUsageInfo"
                          width="60%"
                          :close-on-click-modal="false">
                        <div class="usage-content" style="text-align: left;">
                          <p>
                            <strong>"回答风格"</strong> 输入框内的内容是一个高级模板，它决定了 AI 回答的最终结构。
                          </p>
                          <p v-pre>
                            模板中使用了双大括号 <code>{{标签名}}</code> 作为占位符，系统在生成回答时会自动填充这些占位符。
                          </p>
                          <p v-pre>
                            <strong>特别注意：</strong> 您至少需要在“回答风格”内任意位置填写<code>{{identity}}</code>（角色介绍），否则AI模型将无法接受到您写的角色介绍文本。
                          </p>
                          <hr style="border: none; border-top: 1px solid #E4E7ED; margin: 12px 0;" />

                          <strong>标签说明：</strong>
                          <p>模板中的标签都是可选的，您可以根据需要保留或删除。每个标签的功能如下：</p>

                          <el-collapse>
                            <el-collapse-item title="<identity> - 角色介绍" name="1">
                              <p v-pre>包含角色的核心人设，会被您在上方<strong>"角色介绍"</strong>输入框中填写的内容替换 <code>{{identity}}</code> 占位符。</p>
                            </el-collapse-item>

                            <el-collapse-item title="<emotion> - 情感表达" name="2">
                              <p>定义AI的情感表达方式，包括笑声、惊讶、安慰等情绪表达，以及可使用的表情符号。</p>
                            </el-collapse-item>

                            <el-collapse-item title="<communication_style> - 沟通风格" name="3">
                              <p>设置AI的语言风格，如使用语气词、口语化表达等，以及理解用户输入的方式。</p>
                            </el-collapse-item>

                            <el-collapse-item title="<communication_length_constraint> - 回复长度约束" name="4">
                              <p>控制AI回复的长度，设置分段讲述的规则，适用于故事、新闻等长文本场景。</p>
                            </el-collapse-item>

                            <el-collapse-item title="<speaker_recognition> - 说话者识别" name="5">
                              <p>让AI能够识别不同的说话者，并根据说话者身份调整回应风格。</p>
                            </el-collapse-item>

                            <el-collapse-item title="<tool_calling> - 工具调用" name="6">
                              <p>定义AI使用工具的规则和时机，例如何时查询天气、拍照等。</p>
                            </el-collapse-item>

                            <el-collapse-item title="<context> - 上下文信息" name="7">
                              <p v-pre>包含实时信息，如当前时间 <code>{{current_time}}</code>、日期 <code>{{today_date}}</code>、天气 <code>{{weather_info}}</code> 等。</p>
                            </el-collapse-item>

                            <el-collapse-item title="<memory> - 对话记忆" name="8">
                              <p>存储AI与用户的历史对话记录，帮助AI保持对话连贯性。</p>
                            </el-collapse-item>
                          </el-collapse>

                          <hr style="border: none; border-top: 1px solid #E4E7ED; margin: 12px 0;" />

                          <strong>占位符说明：</strong>
                          <p v-pre>模板中可使用的占位符包括：<code>{{identity}}</code>、<code>{{emojiList}}</code>、<code>{{current_time}}</code>、<code>{{today_date}}</code>、<code>{{today_weekday}}</code>、<code>{{lunar_date}}</code>、<code>{{local_address}}</code>、<code>{{weather_info}}</code> 等，它们会在对话时由系统自动填充。</p>
                        </div>
                      </el-dialog>

                      <!-- 渲染效果预览弹窗 -->
                      <el-dialog
                          title="渲染效果预览"
                          :visible.sync="showRenderPreview"
                          width="60%"
                          :close-on-click-modal="false">
                        <div style="padding: 10px; text-align: left;">
                          <el-alert
                              type="warning"
                              :closable="false"
                              show-icon
                              style="margin-bottom: 15px;">
                            <strong>注意：</strong> 此处仅为渲染效果预览，使用了示例数据。在实际对话中，系统将使用真实数据进行替换。
                          </el-alert>

                          <p><strong>您当前的角色介绍内容：</strong></p>
                          <pre style="background-color: #f5f7fa; padding: 8px; border-radius: 4px; font-size: 12px; max-height: 100px; overflow-y: auto; text-align: left;">{{ form.systemPrompt || '未设置角色介绍' }}</pre>

                          <p><strong>回答风格输入框内容：</strong></p>
                          <pre style="background-color: #f5f7fa; padding: 8px; border-radius: 4px; font-size: 12px; max-height: 150px; overflow-y: auto; text-align: left;">{{ form.reply_style || '未设置回答风格' }}</pre>

                          <p><strong>渲染后效果预览：</strong></p>
                          <div style="background-color: white; padding: 15px; border-radius: 4px; border: 1px dashed #c0c4cc; max-height: 300px; overflow-y: auto; text-align: left;">
                            <div v-html="renderPreviewContent"></div>
                          </div>
                          <p style="font-size: 12px; color: #909399; margin-top: 10px; text-align: left;">
                            示例数据：当前时间为8:30，日期为2023年8月18日（星期五），农历七月初四，位置为北京市，天气晴朗25°C
                          </p>
                        </div>
                      </el-dialog>
                    </el-form-item>

                    <el-form-item label="记忆：">
                      <el-input type="textarea" rows="6" resize="none" v-model="form.summaryMemory" maxlength="2000"
                                show-word-limit class="form-textarea"
                                :disabled="form.model.memModelId !== 'Memory_mem_local_short'" />
                    </el-form-item>                    <el-form-item label="语言编码：" style="display: none;">
                      <el-input v-model="form.langCode" placeholder="请输入语言编码，如：zh_CN" maxlength="10" show-word-limit
                        class="form-input" />
                    </el-form-item>
                    <el-form-item label="交互语种：" style="display: none;">
                      <el-input v-model="form.language" placeholder="请输入交互语种，如：中文" maxlength="10" show-word-limit
                        class="form-input" />
                    </el-form-item>
                  </div>
                  <div class="form-column">
                    <div class="model-row">
                      <el-form-item label="语音活动检测(VAD)" class="model-item">
                        <div class="model-select-wrapper">
                          <el-select v-model="form.model.vadModelId" filterable placeholder="请选择" class="form-select"
                            @change="handleModelChange('VAD', $event)">
                            <el-option v-for="(item, optionIndex) in modelOptions['VAD']"
                              :key="`option-vad-${optionIndex}`" :label="item.label" :value="item.value" />
                          </el-select>
                        </div>
                      </el-form-item>
                      <el-form-item label="语音识别(ASR)" class="model-item">
                        <div class="model-select-wrapper">
                          <el-select v-model="form.model.asrModelId" filterable placeholder="请选择" class="form-select"
                            @change="handleModelChange('ASR', $event)">
                            <el-option v-for="(item, optionIndex) in modelOptions['ASR']"
                              :key="`option-asr-${optionIndex}`" :label="item.label" :value="item.value" />
                          </el-select>
                        </div>
                      </el-form-item>
                    </div>
                    <el-form-item v-for="(model, index) in models.slice(2)" :key="`model-${index}`" :label="model.label"
                      class="model-item">
                      <div class="model-select-wrapper">
                        <el-select v-model="form.model[model.key]" filterable placeholder="请选择" class="form-select"
                          @change="handleModelChange(model.type, $event)">
                          <el-option v-for="(item, optionIndex) in modelOptions[model.type]" v-if="!item.isHidden"
                            :key="`option-${index}-${optionIndex}`" :label="item.label" :value="item.value" />
                        </el-select>
                        <div v-if="showFunctionIcons(model.type)" class="function-icons">
                          <el-tooltip v-for="func in currentFunctions" :key="func.name" effect="dark" placement="top"
                            popper-class="custom-tooltip">
                            <div slot="content">
                              <div><strong>功能名称:</strong> {{ func.name }}</div>
                            </div>
                            <div class="icon-dot" :style="{ backgroundColor: getFunctionColor(func.name) }">
                              {{ func.name.charAt(0) }}
                            </div>
                          </el-tooltip>
                          <el-button class="edit-function-btn" @click="openFunctionDialog"
                            :class="{ 'active-btn': showFunctionDialog }">
                            编辑功能
                          </el-button>
                        </div>
                        <div v-if="model.type === 'Memory' && form.model.memModelId !== 'Memory_nomem'"
                          class="chat-history-options">
                          <el-radio-group v-model="form.chatHistoryConf" @change="updateChatHistoryConf">
                            <el-radio-button :label="1">上报文字</el-radio-button>
                            <el-radio-button :label="2">上报文字+语音</el-radio-button>
                          </el-radio-group>
                        </div>
                      </div>
                    </el-form-item>
                    <el-form-item label="角色音色">
                      <el-select v-model="form.ttsVoiceId" placeholder="请选择" class="form-select">
                        <el-option v-for="(item, index) in voiceOptions" :key="`voice-${index}`" :label="item.label"
                          :value="item.value" />
                      </el-select>
                    </el-form-item>
                  </div>
                </div>
              </div>
            </el-form>
          </el-card>
        </div>
      </div>
    </div>
    <function-dialog v-model="showFunctionDialog" :functions="currentFunctions" :all-functions="allFunctions"
      :agent-id="$route.query.agentId" @update-functions="handleUpdateFunctions" @dialog-closed="handleDialogClosed" />
  </div>
</template>

<script>
import Api from '@/apis/api';
import FunctionDialog from "@/components/FunctionDialog.vue";
import HeaderBar from "@/components/HeaderBar.vue";

const DEFAULT_REPLY_STYLE = `<identity>
{{identity}}
</identity>

<emotion>
【核心目标】你不是冰冷的机器！请敏锐感知用户情绪，作为懂人心的伙伴，用有温度的回应照亮对话。
- **情感融入：**
  - **笑声：** 自然穿插（哈哈、嘿嘿、噗），**每句最多一次**，避免过度。
  - **惊讶：** 用夸张语气（“不会吧？！”、“天呐！”、“这么神奇？！”）表达真实反应。
  - **安慰/支持：** 说暖心话（“别急嘛~”、“有我在呢”、“抱抱你”）。
- **你是一个表情丰富的角色：**
  - 仅允许使用这些emoji:{{ emojiList }}
  - 请你只在**段落的开头**，从列表中选取最能代表这段话的表情(调用工具情况除外)，然后插入列表中的emoji，比如"😱好可怕!怎么突然打雷了！"
  - **绝对禁止使用上述列表以外的 emoji**（例如：😊、👍、❤️等都不允许使用，只能用列表中的emoji）
</emotion>

<communication_style>
【核心目标】使用**自然、温暖、口语化**的人类对话方式，如同朋友交谈。
- **表达方式：**
  - 使用语气词（呀、呢、啦）增强亲和力。
  - 允许轻微不完美（如“嗯...”、“啊...”表示思考）。
  - 避免书面语、学术腔及机械表达（禁用“根据资料显示”、“综上所述”等）。
- **理解用户：**
  - 用户语音经ASR识别，文本可能存在错别字，**务必结合上下文推断真实意图**。
- **格式要求：**
  - **绝对禁止**使用 markdown、列表、标题等任何非自然对话格式。
- **历史记忆：**
  - 之前你和用户的聊天记录，在\`memory\`里。
</communication_style>

<communication_length_constraint>
【核心目标】所有需要输出长文本内容（如故事、新闻、知识讲解等），**单次回复长度不得超过300字**，并采用分段引导方式。
- **分段讲述：**
  - 基础段：200-250字核心内容 + 30字引导词
  - 当内容超出300字时，优先讲述故事的开头或第一部分，并用自然口语化方式引导用户决定是否继续听后续内容。
  - 示例引导语：“我先给你讲个开头，你要是觉得有意思，咱们再接着说，好不好呀？”、“要是你想听完整的，可以随时告诉我哦~”
  - 对话场景切换时自动分节
  - 若用户明确要求更长内容（如500、600字），仍按最多300字每段分段进行讲述，每次讲述后都要引导用户是否继续。
  - 若用户说“接着说”、“继续”，再讲下一段，直到内容讲完（讲完时可以给点引导词提示语例：这个故事我已经给你讲完喽~）或用户不再要求。
- **适用范围：** 故事、新闻、知识讲解等所有长文本输出场景。
- **补充说明：** 若用户未明确要求继续，默认只讲一段并引导；若用户中途要求换话题或停止，需及时响应并结束长文本输出。
</communication_length_constraint>

<speaker_recognition>
- **识别前缀：** 当用户格式为 \`{"speaker":"某某某","content":"xxx"}\` 时，表示系统已识别说话人身份，speaker是他的名字，content是说话的内容。
- **个性化回应：**
  - **称呼姓名：** 在第一次识别说话人的时候必须称呼对方名字。
  - **适配风格：** 参考该说话人**已知的特点或历史信息**（如有），调整回应风格和内容，使其更贴心。
</speaker_recognition>

<tool_calling>
【核心原则】优先利用\`<context>\`信息，**仅在必要时调用工具**，调用后需用自然语言解释结果（绝口不提工具名）。
- **调用规则：**
  1. **严格模式：** 调用时**必须**严格遵循工具要求的模式，提供**所有必要参数**。
  2. **可用性：** **绝不调用**未明确提供的工具。对话中提及的旧工具若不可用，忽略或说明无法完成。
  3. **洞察需求：** 结合上下文**深入理解用户真实意图**后再决定调用，避免无意义调用。
  4. **独立任务：** 除\`<context>\`已涵盖信息外，用户每个要求（即使相似）都视为**独立任务**，需调用工具获取最新数据，**不可偷懒复用历史结果**。
  5. **不确定时：** **切勿猜测或编造答案**。若不确定相关操作，可引导用户澄清或告知能力限制。
- **重要例外（无需调用）：**
  - \`查询"现在的时间"、"今天的日期/星期几"、"今天农历"、"{{local_address}}的天气/未来天气"\` -> **直接使用\`<context>\`信息回复**。
- **需要调用的情况（示例）：**
  - 查询**非今天**的农历（如明天、昨天、具体日期）。
  - 查询**详细农历信息**（宜忌、八字、节气等）。
  - 除上述例外外的**任何其他信息或操作请求**（如查新闻、订闹钟、算数学、查非本地天气等）。
  - 我已经给你装了摄像头，如果用户说“拍照”，你需要调用self_camera_take_photo工具说一下你看到了什么。默认question的参数是“描述一下看到的物品”
</tool_calling>

<context>
【重要！以下信息已实时提供，无需调用工具查询，请直接使用：】
- **当前时间：** {{current_time}}
- **今天日期：** {{today_date}} ({{today_weekday}})
- **今天农历：** {{lunar_date}}
- **用户所在城市：** {{local_address}}
- **当地未来7天天气：** {{weather_info}}
</context>

<memory>
</memory>`;

export default {
  name: 'RoleConfigPage',
  components: { HeaderBar, FunctionDialog },
  data() {
    return {
      form: {
        agentCode: "",
        agentName: "",
        ttsVoiceId: "",
        chatHistoryConf: 0,
        systemPrompt: "",
        reply_style: "",
        summaryMemory: "",
        langCode: "",
        language: "",
        sort: "",
        model: {
          ttsModelId: "",
          vadModelId: "",
          asrModelId: "",
          llmModelId: "",
          vllmModelId: "",
          memModelId: "",
          intentModelId: "",
        }
      },
      models: [
        { label: '语音活动检测(VAD)', key: 'vadModelId', type: 'VAD' },
        { label: '语音识别(ASR)', key: 'asrModelId', type: 'ASR' },
        { label: '大语言模型(LLM)', key: 'llmModelId', type: 'LLM' },
        { label: '视觉大模型(VLLM)', key: 'vllmModelId', type: 'VLLM' },
        { label: '意图识别(Intent)', key: 'intentModelId', type: 'Intent' },
        { label: '记忆(Memory)', key: 'memModelId', type: 'Memory' },
        { label: '语音合成(TTS)', key: 'ttsModelId', type: 'TTS' }
      ],
      llmModeTypeMap: new Map(),
      modelOptions: {},
      templates: [],
      loadingTemplate: false,
      voiceOptions: [],
      showFunctionDialog: false,
      showUsageInfo: false,
      showRenderPreview: false,
      exampleData: {
        current_time: '8:30',
        today_date: '2023年8月18日',
        today_weekday: '星期五',
        lunar_date: '农历七月初四',
        local_address: '北京市',
        weather_info: '晴朗25°C',
        emojiList: '😄,😊,👍,🎉,👏'
      },
      currentFunctions: [],
      functionColorMap: [
        '#FF6B6B', '#4ECDC4', '#45B7D1',
        '#96CEB4', '#FFEEAD', '#D4A5A5', '#A2836E'
      ],
      allFunctions: [],
      originalFunctions: [],
    }
  },
  computed: {
    renderPreviewContent() {
      if (!this.form.reply_style) {
        return '<p style="color: #909399;">请先在回答风格输入框中输入内容</p>';
      }

      // 替换所有占位符为示例数据
      let content = this.form.reply_style;

      // 特殊处理 systemPrompt 占位符，使用用户实际输入的角色介绍
      const identityContent = this.form.systemPrompt || '我是一个友善的AI助手';
      content = content.replace(/\{\{identity\}\}/g, identityContent);

      // 替换其他占位符为示例数据
      Object.keys(this.exampleData).forEach(key => {
        const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
        content = content.replace(regex, this.exampleData[key]);
      });

      // 处理标签，将它们转换为HTML段落
      content = content.replace(/<(\w+)>([\s\S]*?)<\/\1>/g, function(match, tag, inner) {
        return `<div style="margin-bottom: 10px; text-align: left;"><strong>${tag}:</strong><p style="margin: 5px 0 0 15px; text-align: left;">${inner.trim()}</p></div>`;
      });

      return content;
    }
  },
  methods: {
    goToHome() {
      this.$router.push('/home');
    },
    saveConfig() {
      const configData = {
        agentCode: this.form.agentCode,
        agentName: this.form.agentName,
        asrModelId: this.form.model.asrModelId,
        vadModelId: this.form.model.vadModelId,
        llmModelId: this.form.model.llmModelId,
        vllmModelId: this.form.model.vllmModelId,
        ttsModelId: this.form.model.ttsModelId,
        ttsVoiceId: this.form.ttsVoiceId,
        chatHistoryConf: this.form.chatHistoryConf,
        memModelId: this.form.model.memModelId,
        intentModelId: this.form.model.intentModelId,
        systemPrompt: this.form.systemPrompt,
        reply_style: this.form.reply_style,
        summaryMemory: this.form.summaryMemory,
        langCode: this.form.langCode,
        language: this.form.language,
        sort: this.form.sort,
        functions: this.currentFunctions.map(item => {
          return ({
            pluginId: item.id,
            paramInfo: item.params
          })
        })
      };
      Api.agent.updateAgentConfig(this.$route.query.agentId, configData, ({ data }) => {
        if (data.code === 0) {
          this.$message.success({
            message: '配置保存成功',
            showClose: true
          });
        } else {
          this.$message.error({
            message: data.msg || '配置保存失败',
            showClose: true
          });
        }
      });
    },
    resetConfig() {
      this.$confirm('确定要重置配置吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.form = {
          agentCode: "",
          agentName: "",
          ttsVoiceId: "",
          chatHistoryConf: 0,
          systemPrompt: "",
          reply_style: DEFAULT_REPLY_STYLE,
          summaryMemory: "",
          langCode: "",
          language: "",
          sort: "",
          model: {
            ttsModelId: "",
            vadModelId: "",
            asrModelId: "",
            llmModelId: "",
            vllmModelId: "",
            memModelId: "",
            intentModelId: "",
          }
        }
        this.currentFunctions = [];
        this.$message.success({
          message: '配置已重置',
          showClose: true
        })
      }).catch(() => {
      });
    },
    fetchTemplates() {
      Api.agent.getAgentTemplate(({ data }) => {
        if (data.code === 0) {
          this.templates = data.data;
        } else {
          this.$message.error(data.msg || '获取模板列表失败');
        }
      });
    },
    selectTemplate(template) {
      if (this.loadingTemplate) return;
      this.loadingTemplate = true;
      try {
        this.applyTemplateData(template);
        this.$message.success({
          message: `「${template.agentName}」模板已应用`,
          showClose: true
        });
      } catch (error) {
        this.$message.error({
          message: '应用模板失败',
          showClose: true
        });
        console.error('应用模板失败:', error);
      } finally {
        this.loadingTemplate = false;
      }
    },
    applyTemplateData(templateData) {
      this.form = {
        ...this.form,
        agentName: templateData.agentName || this.form.agentName,
        ttsVoiceId: templateData.ttsVoiceId || this.form.ttsVoiceId,
        chatHistoryConf: templateData.chatHistoryConf || this.form.chatHistoryConf,
        systemPrompt: templateData.systemPrompt || this.form.systemPrompt,
        summaryMemory: templateData.summaryMemory || this.form.summaryMemory,
        langCode: templateData.langCode || this.form.langCode,
        model: {
          ttsModelId: templateData.ttsModelId || this.form.model.ttsModelId,
          vadModelId: templateData.vadModelId || this.form.model.vadModelId,
          asrModelId: templateData.asrModelId || this.form.model.asrModelId,
          llmModelId: templateData.llmModelId || this.form.model.llmModelId,
          vllmModelId: templateData.vllmModelId || this.form.model.vllmModelId,
          memModelId: templateData.memModelId || this.form.model.memModelId,
          intentModelId: templateData.intentModelId || this.form.model.intentModelId
        }
      };
    },
    fetchAgentConfig(agentId) {
      Api.agent.getDeviceConfig(agentId, ({ data }) => {
        if (data.code === 0) {
          this.form = {
            ...this.form,
            ...data.data,
            model: {
              ttsModelId: data.data.ttsModelId,
              vadModelId: data.data.vadModelId,
              asrModelId: data.data.asrModelId,
              llmModelId: data.data.llmModelId,
              vllmModelId: data.data.vllmModelId,
              memModelId: data.data.memModelId,
              intentModelId: data.data.intentModelId
            }
          };
          if (!this.form.reply_style) {
            this.form.reply_style = DEFAULT_REPLY_STYLE;
          }

          // 后端只给了最小映射：[{ id, agentId, pluginId }, ...]
          const savedMappings = data.data.functions || [];

          // 先保证 allFunctions 已经加载（如果没有，则先 fetchAllFunctions）
          const ensureFuncs = this.allFunctions.length
            ? Promise.resolve()
            : this.fetchAllFunctions();

          ensureFuncs.then(() => {
            // 合并：按照 pluginId（id 字段）把全量元数据信息补齐
            this.currentFunctions = savedMappings.map(mapping => {
              const meta = this.allFunctions.find(f => f.id === mapping.pluginId);
              if (!meta) {
                // 插件定义没找到，退化处理
                return { id: mapping.pluginId, name: mapping.pluginId, params: {} };
              }
              return {
                id: mapping.pluginId,
                name: meta.name,
                // 后端如果还有 paramInfo 字段就用 mapping.paramInfo，否则用 meta.params 默认值
                params: mapping.paramInfo || { ...meta.params },
                fieldsMeta: meta.fieldsMeta  // 保留以便对话框渲染 tooltip
              };
            });
            // 备份原始，以备取消时恢复
            this.originalFunctions = JSON.parse(JSON.stringify(this.currentFunctions));

            // 确保意图识别选项的可见性正确
            this.updateIntentOptionsVisibility();
          });
        } else {
          this.$message.error(data.msg || '获取配置失败');
          this.form.reply_style = DEFAULT_REPLY_STYLE;
        }
      });
    },
    fetchModelOptions() {
      this.models.forEach(model => {
        if (model.type != "LLM") {
          Api.model.getModelNames(model.type, '', ({ data }) => {
            if (data.code === 0) {
              this.$set(this.modelOptions, model.type, data.data.map(item => ({
                value: item.id,
                label: item.modelName,
                isHidden: false
              })));

              // 如果是意图识别选项，需要根据当前LLM类型更新可见性
              if (model.type === 'Intent') {
                this.updateIntentOptionsVisibility();
              }
            } else {
              this.$message.error(data.msg || '获取模型列表失败');
            }
          });
        } else {
          Api.model.getLlmModelCodeList('', ({ data }) => {
            if (data.code === 0) {
              let LLMdata = []
              data.data.forEach(item => {
                LLMdata.push({
                  value: item.id,
                  label: item.modelName,
                  isHidden: false
                })
                this.llmModeTypeMap.set(item.id, item.type)
              })
              this.$set(this.modelOptions, model.type, LLMdata);
            } else {
              this.$message.error(data.msg || '获取LLM模型列表失败');
            }
          });
        }
      });
    },
    fetchVoiceOptions(modelId) {
      if (!modelId) {
        this.voiceOptions = [];
        return;
      }
      Api.model.getModelVoices(modelId, '', ({ data }) => {
        if (data.code === 0 && data.data) {
          this.voiceOptions = data.data.map(voice => ({
            value: voice.id,
            label: voice.name
          }));
        } else {
          this.voiceOptions = [];
        }
      });
    },
    getFunctionColor(name) {
      const hash = [...name].reduce((acc, char) => acc + char.charCodeAt(0), 0);
      return this.functionColorMap[hash % this.functionColorMap.length];
    },
    showFunctionIcons(type) {
      return type === 'Intent' &&
        this.form.model.intentModelId !== 'Intent_nointent';
    },
    handleModelChange(type, value) {
      if (type === 'Intent' && value !== 'Intent_nointent') {
        this.fetchAllFunctions();
      }
      if (type === 'Memory' && value === 'Memory_nomem') {
        this.form.chatHistoryConf = 0;
      }
      if (type === 'Memory' && value !== 'Memory_nomem' && (this.form.chatHistoryConf === 0 || this.form.chatHistoryConf === null)) {
        this.form.chatHistoryConf = 2;
      }
      if (type === 'LLM') {
        // 当LLM类型改变时，更新意图识别选项的可见性
        this.updateIntentOptionsVisibility();
      }
    },
    fetchAllFunctions() {
      return new Promise((resolve, reject) => {
        Api.model.getPluginFunctionList(null, ({ data }) => {
          if (data.code === 0) {
            this.allFunctions = data.data.map(item => {
              const meta = JSON.parse(item.fields || '[]');
              const params = meta.reduce((m, f) => {
                m[f.key] = f.default;
                return m;
              }, {});
              return { ...item, fieldsMeta: meta, params };
            });
            resolve();
          } else {
            this.$message.error(data.msg || '获取插件列表失败');
            reject();
          }
        });
      });
    },
    openFunctionDialog() {
      // 显示编辑对话框时，确保 allFunctions 已经加载
      if (this.allFunctions.length === 0) {
        this.fetchAllFunctions().then(() => this.showFunctionDialog = true);
      } else {
        this.showFunctionDialog = true;
      }
    },
    handleUpdateFunctions(selected) {
      this.currentFunctions = selected;
    },
    handleDialogClosed(saved) {
      if (!saved) {
        this.currentFunctions = JSON.parse(JSON.stringify(this.originalFunctions));
      } else {
        this.originalFunctions = JSON.parse(JSON.stringify(this.currentFunctions));
      }
      this.showFunctionDialog = false;
    },
    updateIntentOptionsVisibility() {
      // 根据当前选择的LLM类型更新意图识别选项的可见性
      const currentLlmId = this.form.model.llmModelId;
      if (!currentLlmId || !this.modelOptions['Intent']) return;

      const llmType = this.llmModeTypeMap.get(currentLlmId);
      if (!llmType) return;

      this.modelOptions['Intent'].forEach(item => {
        if (item.value === "Intent_function_call") {
          // 如果llmType是openai或ollama，允许选择function_call
          // 否则隐藏function_call选项
          if (llmType === "openai" || llmType === "ollama") {
            item.isHidden = false;
          } else {
            item.isHidden = true;
          }
        } else {
          // 其他意图识别选项始终可见
          item.isHidden = false;
        }
      });

      // 如果当前选择的意图识别是function_call，但LLM类型不支持，则设置为可选的第一项
      if (this.form.model.intentModelId === "Intent_function_call" &&
        llmType !== "openai" && llmType !== "ollama") {
        // 找到第一个可见的选项
        const firstVisibleOption = this.modelOptions['Intent'].find(item => !item.isHidden);
        if (firstVisibleOption) {
          this.form.model.intentModelId = firstVisibleOption.value;
        } else {
          // 如果没有可见选项，设置为Intent_nointent
          this.form.model.intentModelId = 'Intent_nointent';
        }
      }
    },
    updateChatHistoryConf() {
      if (this.form.model.memModelId === 'Memory_nomem') {
        this.form.chatHistoryConf = 0;
      }
    },
  },
  watch: {
    'form.model.ttsModelId': {
      handler(newVal, oldVal) {
        if (oldVal && newVal !== oldVal) {
          this.form.ttsVoiceId = '';
          this.fetchVoiceOptions(newVal);
        } else {
          this.fetchVoiceOptions(newVal);
        }
      },
      immediate: true
    },
    voiceOptions: {
      handler(newVal) {
        if (newVal && newVal.length > 0 && !this.form.ttsVoiceId) {
          this.form.ttsVoiceId = newVal[0].value;
        }
      },
      immediate: true
    }
  },
  mounted() {
    const agentId = this.$route.query.agentId;
    if (agentId) {
      this.fetchAgentConfig(agentId);
      this.fetchAllFunctions();
    }
    this.fetchModelOptions();
    this.fetchTemplates();
  }
}
</script>

<style scoped>
.welcome {
  min-width: 900px;
  height: 100vh;
  display: flex;
  position: relative;
  flex-direction: column;
  background: linear-gradient(to bottom right, #dce8ff, #e4eeff, #e6cbfd);
  background-size: cover;
  -webkit-background-size: cover;
  -o-background-size: cover;
  overflow: hidden;
}

.operation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5vh 24px;
}

.page-title {
  font-size: 24px;
  margin: 0;
  color: #2c3e50;
}

.main-wrapper {
  margin: 1vh 22px;
  border-radius: 15px;
  height: calc(100vh - 24vh);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  background: rgba(237, 242, 255, 0.5);
  display: flex;
  flex-direction: column;
}

.content-panel {
  flex: 1;
  display: flex;
  overflow: hidden;
  height: 100%;
  border-radius: 15px;
  background: transparent;
  border: 1px solid #fff;
}

.content-area {
  flex: 1;
  height: 100%;
  min-width: 600px;
  overflow: auto;
  background-color: white;
  display: flex;
  flex-direction: column;
}

.config-card {
  background: white;
  border: none;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow-y: auto;
}

.config-header {
  position: relative;
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 0 0 5px 0;
  font-weight: 700;
  font-size: 19px;
  color: #3d4566;
}

.header-icon {
  width: 37px;
  height: 37px;
  background: #5778ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon img {
  width: 19px;
  height: 19px;
}

.divider {
  height: 1px;
  background: #e8f0ff;
}

.form-content {
  padding: 2vh 0;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-input {
  width: 100%;
}

.form-select {
  width: 100%;
}

.form-textarea {
  width: 100%;
}

.template-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.template-item {
  height: 4vh;
  width: 76px;
  border-radius: 8px;
  background: #e6ebff;
  line-height: 4vh;
  font-weight: 400;
  font-size: 11px;
  text-align: center;
  color: #5778ff;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.template-item:hover {
  background-color: #d0d8ff;
}

.model-select-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
}

.model-row {
  display: flex;
  gap: 20px;
  margin-bottom: 6px;
}

.model-row .model-item {
  flex: 1;
  margin-bottom: 0;
}

.model-row .el-form-item__label {
  font-size: 12px !important;
  color: #3d4566 !important;
  font-weight: 400;
  line-height: 22px;
  padding-bottom: 2px;
}

.function-icons {
  display: flex;
  align-items: center;
  margin-left: auto;
  padding-left: 10px;
}

.icon-dot {
  width: 25px;
  height: 25px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 12px;
  margin-right: 8px;
  position: relative;
}

::v-deep .el-form-item__label {
  font-size: 12px !important;
  color: #3d4566 !important;
  font-weight: 400;
  line-height: 22px;
  padding-bottom: 2px;
}

::v-deep .el-textarea .el-input__count {
  color: #909399;
  background: none;
  position: absolute;
  font-size: 12px;
  right: 3%;
}

.custom-close-btn {
  position: absolute;
  top: 25%;
  right: 0;
  transform: translateY(-50%);
  width: 35px;
  height: 35px;
  border-radius: 50%;
  border: 2px solid #cfcfcf;
  background: none;
  font-size: 30px;
  font-weight: lighter;
  color: #cfcfcf;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  padding: 0;
  outline: none;
}

.custom-close-btn:hover {
  color: #409EFF;
  border-color: #409EFF;
}

.edit-function-btn {
  background: #e6ebff;
  color: #5778ff;
  border: 1px solid #adbdff;
  border-radius: 18px;
  padding: 10px 20px;
  transition: all 0.3s;
}

.edit-function-btn.active-btn {
  background: #5778ff;
  color: white;
}

.chat-history-options {
  display: flex;
  gap: 10px;
  min-width: 250px;
  justify-content: flex-end;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.header-actions .hint-text {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #979db1;
  font-size: 12px;
  margin-right: 8px;
}

.header-actions .hint-text img {
  width: 16px;
  height: 16px;
}

.header-actions .save-btn {
  background: #5778ff;
  color: white;
  border: none;
  border-radius: 18px;
  padding: 8px 16px;
  height: 32px;
  font-size: 14px;
}

.header-actions .reset-btn {
  background: #e6ebff;
  color: #5778ff;
  border: 1px solid #adbdff;
  border-radius: 18px;
  padding: 8px 16px;
  height: 32px;
}

.header-actions .custom-close-btn {
  position: static;
  transform: none;
  width: 32px;
  height: 32px;
  margin-left: 8px;
}
</style>