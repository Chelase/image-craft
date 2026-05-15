# Image Craft 开发计划

> 参考 ui-ux-pro-max 技能架构，为 image-craft 添加风格系统和提示词库

## 📋 项目愿景

将 image-craft 从简单的 API 调用工具升级为**智能图像生成助手**，内置：
- 预定义艺术风格库
- 提示词模板库
- 色彩方案参考
- 智能推荐系统

---

## 🎯 开发阶段

### Phase 1: 基础数据层 ⏳

#### 1.1 创建风格数据库
- [ ] 设计 CSV/JSON 数据结构
- [ ] 收集并整理艺术风格数据（目标：50+ 种风格）
- [ ] 每种风格包含：
  - 风格名称（中英文）
  - 风格描述
  - 关键词标签
  - 示例提示词
  - 适用场景
  - 推荐参数

**风格分类：**
| 类别 | 示例风格 |
|------|----------|
| 传统艺术 | 油画、水彩、素描、版画、国画 |
| 数字艺术 | 像素风、赛博朋克、蒸汽波、故障艺术 |
| 摄影风格 | 胶片、宝丽来、黑白、长曝光、微距 |
| 插画风格 | 扁平、等距、日系、美漫、儿童插画 |
| 3D 渲染 | 低多边形、体素、C4D 风格、Blender 风格 |
| 特殊效果 | 双重曝光、光绘、红外摄影、移轴摄影 |

#### 1.2 创建提示词模板库
- [ ] 设计模板数据结构
- [ ] 收集常用提示词模式（目标：100+ 模板）
- [ ] 模板分类：
  - 场景模板（风景、人物、产品、抽象）
  - 风格修饰词
  - 光影描述词
  - 构图指令
  - 质量增强词

**模板结构示例：**
```json
{
  "id": "portrait-cinematic",
  "name": "电影感人像",
  "category": "portrait",
  "template": "A cinematic portrait of {subject}, {lighting}, {mood}, shot on 35mm film, shallow depth of field, dramatic lighting",
  "variables": ["subject", "lighting", "mood"],
  "examples": [...],
  "tags": ["portrait", "cinematic", "film"]
}
```

#### 1.3 创建色彩方案库
- [ ] 设计色彩数据结构
- [ ] 收集经典配色方案（目标：30+ 方案）
- [ ] 包含内容：
  - 方案名称
  - 主色调/辅助色/强调色
  - 适用场景
  - 情感联想
  - 提示词描述

---

### Phase 2: 搜索引擎 ⏳

#### 2.1 Python 搜索脚本
- [ ] 创建 `scripts/search.py`
- [ ] 实现功能：
  - 按关键词搜索风格
  - 按类别筛选
  - 模糊匹配
  - 随机推荐
  - 组合查询

**命令行接口设计：**
```bash
# 搜索风格
python scripts/search.py "水彩" --domain style

# 搜索提示词模板
python scripts/search.py "人像 电影感" --domain prompt

# 获取随机推荐
python scripts/search.py --random --domain style

# 获取完整设计系统
python scripts/search.py "赛博朋克 未来城市" --design-system
```

#### 2.2 智能推荐
- [ ] 基于用户输入推荐风格
- [ ] 风格组合建议
- [ ] 参数优化建议

---

### Phase 3: 集成与增强 ⏳

#### 3.1 更新主脚本
- [ ] 在 `image_craft.py` 中集成搜索功能
- [ ] 添加 `--style` 参数
- [ ] 添加 `--template` 参数
- [ ] 添加 `--suggest` 参数

**增强后的命令行：**
```bash
# 使用预定义风格
python scripts/image_craft.py generate --style "赛博朋克" --subject "东京街头"

# 使用提示词模板
python scripts/image_craft.py generate --template "portrait-cinematic" --var subject="女孩" --var lighting="侧光"

# 获取建议
python scripts/image_craft.py suggest "我想画一个未来城市"
```

#### 3.2 更新 SKILL.md
- [ ] 添加风格系统文档
- [ ] 添加使用示例
- [ ] 更新工作流程

#### 3.3 更新 README
- [ ] 添加风格库介绍
- [ ] 添加提示词库介绍
- [ ] 添加搜索功能说明

---

### Phase 4: 高级功能 ⏳

#### 4.1 提示词优化器
- [ ] 自动增强简单提示词
- [ ] 质量关键词注入
- [ ] 负面提示词生成

#### 4.2 风格混合器
- [ ] 支持多风格组合
- [ ] 风格权重控制
- [ ] 风格迁移

#### 4.3 批量生成
- [ ] 同一提示词多风格变体
- [ ] 风格探索模式
- [ ] A/B 测试支持

---

## 📁 目录结构规划

```
image-craft/
├── SKILL.md
├── README.md
├── README_CN.md
├── ROADMAP.md
├── private_config.json.example
├── .gitignore
├── data/                          # 数据库目录
│   ├── styles.csv                 # 风格数据库
│   ├── prompts.csv                # 提示词模板库
│   ├── colors.csv                 # 色彩方案库
│   └── tags.csv                   # 标签索引
├── scripts/
│   ├── image_craft.py             # 主脚本
│   ├── image_craft.ps1            # PowerShell 脚本
│   └── search.py                  # 搜索引擎
└── examples/                      # 示例目录
    ├── styles/                    # 风格示例图
    └── prompts/                   # 提示词示例
```

---

## 🎨 风格数据库字段设计

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识符 |
| name_en | string | 英文名称 |
| name_cn | string | 中文名称 |
| category | string | 分类 |
| description | string | 描述 |
| keywords | array | 关键词标签 |
| prompt_template | string | 提示词模板 |
| negative_prompt | string | 负面提示词 |
| example_prompt | string | 示例提示词 |
| recommended_params | object | 推荐参数 |
| use_cases | array | 适用场景 |
| difficulty | string | 难度等级 |
| preview_url | string | 预览图链接 |

---

## 📝 提示词模板字段设计

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识符 |
| name | string | 模板名称 |
| category | string | 分类 |
| template | string | 模板内容（含变量） |
| variables | array | 变量列表 |
| examples | array | 使用示例 |
| tags | array | 标签 |
| quality_score | int | 质量评分 (1-5) |

---

## 🚀 里程碑

| 阶段 | 目标 | 预计时间 |
|------|------|----------|
| Phase 1 | 基础数据层完成 | 1-2 周 |
| Phase 2 | 搜索引擎完成 | 1 周 |
| Phase 3 | 集成与增强 | 1 周 |
| Phase 4 | 高级功能 | 2-3 周 |

---

## 💡 灵感来源

- [ui-ux-pro-max](https://github.com/...) - 设计系统数据库架构
- Midjourney - 风格和参数系统
- Stable Diffusion WebUI - 提示词和负面提示词
- DALL-E - 提示词最佳实践

---

## 📌 待讨论

1. 风格数据库用 CSV 还是 JSON？
2. 是否需要支持用户自定义风格？
3. 是否需要风格预览图？
4. 搜索结果排序策略？
5. 是否需要支持多语言提示词生成？
