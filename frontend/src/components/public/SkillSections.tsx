const skillGroups = [
  {
    title: "前端工程",
    items: [
      "React / Vite 页面搭建与组件拆分",
      "聊天框、表单、卡片和响应式布局",
      "Three.js / Canvas 可视化表达",
    ],
  },
  {
    title: "后端接口",
    items: [
      "Python / FastAPI 接口设计",
      "Dify API 代理与密钥隔离",
      "MySQL 数据和媒体元信息管理",
    ],
  },
  {
    title: "AI 应用",
    items: [
      "Dify 工作流和知识库问答",
      "Prompt 编排与岗位匹配回答",
      "AI Agent 业务流程落地思路",
    ],
  },
  {
    title: "交付能力",
    items: [
      "从需求、设计稿到可访问页面",
      "项目截图、视频和文档组织",
      "移动端适配与上线迭代",
    ],
  },
];

export function SkillSections() {
  return (
    <section className="page-shell section" id="skills">
      <div className="section-head">
        <div>
          <p className="eyebrow">能力范围</p>
          <h2>围绕 AI 应用落地组织技术栈。</h2>
        </div>
        {/* <p className="section-note">
          不用百分比自评分，改成“能承担什么工作”，更适合 HR 和技术面试官快速判断。
        </p> */}
      </div>

      <div className="skills-grid">
        {skillGroups.map((group) => (
          <div className="skill-column" key={group.title}>
            <h3>{group.title}</h3>
            <div className="skill-list">
              {group.items.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
