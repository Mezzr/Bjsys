# 备件管理系统 - 后端 API 文档

## 1. API 概览

本系统共需要 **11 个 API 端点**，分为 **3 大模块**：

| 模块 | 端点数 | 功能 |
|------|--------|------|
| 认证模块 (Auth) | 2 | 用户登录、获取当前用户 |
| 备件管理 (Parts) | 5 | 查询、创建、更新、删除备件 |
| 场站管理 (Stations) | 2 | 获取场站列表、获取单个场站 |
| 库存日志 (Inventory) | 2 | 记录库存变化、查询历史 |

---

## 2. 认证模块 (Authentication)

### 2.1 用户登录

**请求**:
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "zhangsan@company.com",
  "password": "password123"
}
```

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "u1",
      "name": "张三",
      "email": "zhangsan@company.com",
      "stationId": "st-001",
      "role": "user"
    }
  }
}
```

**响应 (401)**:
```json
{
  "code": 401,
  "message": "邮箱或密码错误"
}
```

**说明**:
- 用户首次登录需要调用此接口
- 返回的 `token` 需存储到前端 localStorage
- 后续所有请求的 Authorization header 都要带上此 token

---

### 2.2 获取当前用户信息

**请求**:
```
GET /api/auth/me
Authorization: Bearer <token>
```

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "u1",
    "name": "张三",
    "email": "zhangsan@company.com",
    "stationId": "st-001",
    "role": "user",
    "is_active": true,
    "last_login": "2025-12-07T10:30:00Z"
  }
}
```

**响应 (401)**:
```json
{
  "code": 401,
  "message": "token 无效或已过期"
}
```

**说明**:
- 应用启动时调用，验证用户登录状态
- 返回当前登录用户的完整信息
- 如果 token 过期或无效，前端应重定向到登录页

---

## 3. 备件管理模块 (Parts)

### 3.1 获取备件列表

**请求**:
```
GET /api/parts?stationId=st-001&page=1&limit=20&search=滤芯
Authorization: Bearer <token>
```

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `stationId` | string | ✅ | 场站 ID，用于过滤该场站的备件 |
| `page` | number | ❌ | 页码，默认 1 |
| `limit` | number | ❌ | 每页数量，默认 20 |
| `search` | string | ❌ | 搜索关键词（按名称、型号模糊搜索） |
| `status` | string | ❌ | 过滤状态：active, discontinued, archived |

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 105,
    "page": 1,
    "limit": 20,
    "items": [
      {
        "id": "p-001",
        "name": "滤芯 A",
        "model": "XYZ-2000",
        "description": "用于 XYZ 系列机器的空气滤芯",
        "location": "A区第3排第2个柜",
        "supplier": "滤清器有限公司",
        "supplier_code": "SUP-12345",
        "qty": 10,
        "alarmQty": 3,
        "procurementDays": 7,
        "cost": 85.50,
        "retail_price": 120.00,
        "imageUrl": "https://cdn.company.com/images/parts/p-001.jpg",
        "stationId": "st-001",
        "category": "液压",
        "status": "active",
        "created_by": "u1",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_by": "u1",
        "updated_at": "2025-12-06T14:30:00Z",
        "last_purchase_date": "2025-12-01T09:00:00Z",
        "last_use_date": "2025-12-05T16:20:00Z"
      },
      ...
    ]
  }
}
```

**说明**:
- 所有用户都能看到所有场站的备件（无权限限制）
- 前端会根据 `stationId` 请求特定场站的备件
- 服务器端应实现搜索关键词的全文搜索（name, model, description）
- 按 `created_at` 倒序排列，告警备件优先

---

### 3.2 获取单个备件详情

**请求**:
```
GET /api/parts/:id
Authorization: Bearer <token>
```

**URL 参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 备件 ID (UUID) |

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "p-001",
    "name": "滤芯 A",
    "model": "XYZ-2000",
    "description": "用于 XYZ 系列机器的空气滤芯",
    "location": "A区第3排第2个柜",
    "supplier": "滤清器有限公司",
    "supplier_code": "SUP-12345",
    "qty": 10,
    "alarmQty": 3,
    "procurementDays": 7,
    "cost": 85.50,
    "retail_price": 120.00,
    "imageUrl": "https://cdn.company.com/images/parts/p-001.jpg",
    "stationId": "st-001",
    "category": "液压",
    "status": "active",
    "created_by": "u1",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_by": "u1",
    "updated_at": "2025-12-06T14:30:00Z",
    "last_purchase_date": "2025-12-01T09:00:00Z",
    "last_use_date": "2025-12-05T16:20:00Z"
  }
}
```

**响应 (404)**:
```json
{
  "code": 404,
  "message": "备件不存在"
}
```

**说明**:
- 所有用户都能查看任何备件的详情
- 返回完整的备件信息，包括成本价等敏感字段（可选，视权限）

---

### 3.3 创建备件

**请求**:
```
POST /api/parts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "新备件",
  "model": "ABC-123",
  "description": "备件描述",
  "location": "B区1排1柜",
  "supplier": "供应商名称",
  "supplier_code": "SUP-999",
  "qty": 5,
  "alarmQty": 2,
  "procurementDays": 10,
  "cost": 150.00,
  "retail_price": 200.00,
  "imageUrl": "https://cdn.company.com/images/parts/new.jpg",
  "stationId": "st-001",
  "category": "机械",
  "status": "active"
}
```

**请求体字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 备件名称 |
| `model` | string | ✅ | 备件型号 |
| `description` | string | ❌ | 备件描述 |
| `location` | string | ❌ | 存放位置 |
| `supplier` | string | ❌ | 供应商 |
| `supplier_code` | string | ❌ | 供应商备件编号 |
| `qty` | number | ✅ | 当前数量（≥0） |
| `alarmQty` | number | ❌ | 告警阈值（默认 1） |
| `procurementDays` | number | ❌ | 采购周期（天） |
| `cost` | number | ❌ | 单位成本价 |
| `retail_price` | number | ❌ | 零售价格 |
| `imageUrl` | string | ❌ | 图片 URL 或 Data URL |
| `stationId` | string | ✅ | 所属场站 ID |
| `category` | string | ❌ | 备件分类 |
| `status` | string | ❌ | 状态（active/discontinued/archived） |

**响应 (201)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "p-new-001",
    "name": "新备件",
    "model": "ABC-123",
    ...
    "created_at": "2025-12-07T10:30:00Z"
  }
}
```

**响应 (400)**:
```json
{
  "code": 400,
  "message": "备件名称不能为空"
}
```

**响应 (403)**:
```json
{
  "code": 403,
  "message": "无权限在此场站创建备件"
}
```

**权限验证**:
- ✅ 后端必须验证 `user.stationId == stationId`
- ❌ 用户只能在自己的场站创建备件
- 如果违反，返回 403 Forbidden

**说明**:
- `imageUrl` 可以是：
  - 完整 URL: `https://cdn.company.com/...`
  - Data URL: `data:image/jpeg;base64,...` (前端上传的图片)
  - 相对路径: `/images/parts/...`
- 后端应将 Data URL 转换为真实文件并返回文件 URL
- 自动记录 `created_by`, `created_at`

---

### 3.4 更新备件

**请求**:
```
PUT /api/parts/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "qty": 8,
  "alarmQty": 2,
  "location": "A区1排3柜",
  "procurementDays": 7
}
```

**URL 参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 备件 ID (UUID) |

**请求体说明**:
- 支持部分更新（只需传需要更新的字段）
- 可更新字段见上面 3.3 的表格
- 不能修改 `id`, `stationId`, `created_by`, `created_at`

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "p-001",
    "qty": 8,
    "alarmQty": 2,
    "location": "A区1排3柜",
    ...
    "updated_at": "2025-12-07T10:45:00Z"
  }
}
```

**响应 (403)**:
```json
{
  "code": 403,
  "message": "无权限编辑此备件（仅限本场站编辑）"
}
```

**响应 (404)**:
```json
{
  "code": 404,
  "message": "备件不存在"
}
```

**权限验证** ⭐ 重要:
- ✅ 后端必须验证 `user.stationId == part.stationId`
- ❌ 用户只能编辑自己场站的备件
- 如果违反，返回 403 Forbidden
- **前端的权限检查仅为UI优化，后端验证才是真正的安全保障**

**说明**:
- 自动更新 `updated_at` 和 `updated_by`
- 如果库存数量改变，应记录到 `inventory_logs` 表

---

### 3.5 删除备件

**请求**:
```
DELETE /api/parts/:id
Authorization: Bearer <token>
```

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success"
}
```

**响应 (403)**:
```json
{
  "code": 403,
  "message": "无权限删除此备件"
}
```

**响应 (404)**:
```json
{
  "code": 404,
  "message": "备件不存在"
}
```

**权限验证**:
- ✅ 同编辑权限，只能删除本场站备件
- ❌ 如果违反，返回 403 Forbidden

**说明**:
- 前端暂未实现删除功能（可选）
- 建议使用逻辑删除（设置 status = 'archived'）而不是物理删除

---

## 4. 场站管理模块 (Stations)

### 4.1 获取所有场站列表

**请求**:
```
GET /api/stations?is_active=true
Authorization: Bearer <token>
```

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `is_active` | boolean | ❌ | 只返回启用的场站，默认 true |

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": "st-001",
      "name": "station-1",
      "display_name": "华东地区生产中心",
      "location": "江苏省苏州市",
      "phone": "0512-88888888",
      "manager": "李四",
      "manager_email": "lisi@company.com",
      "description": "主要负责华东地区的生产和维护",
      "is_active": true,
      "created_at": "2025-01-01T08:00:00Z",
      "updated_at": "2025-12-07T09:00:00Z"
    },
    {
      "id": "st-002",
      "name": "station-2",
      "display_name": "华南地区维修中心",
      "location": "广东省深圳市",
      "phone": "0755-99999999",
      "manager": "王五",
      "manager_email": "wangwu@company.com",
      "description": "主要负责华南地区的维修和保养",
      "is_active": true,
      "created_at": "2025-01-01T08:00:00Z",
      "updated_at": "2025-12-07T09:00:00Z"
    }
  ]
}
```

**说明**:
- 所有已登录用户都能获取场站列表
- 前端用此列表填充"场站选择"弹窗
- 返回的 `name` 字段对应前端的 `stationId`（如 'station-1'）

---

### 4.2 获取单个场站详情

**请求**:
```
GET /api/stations/:id
Authorization: Bearer <token>
```

**URL 参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 场站 ID |

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "st-001",
    "name": "station-1",
    "display_name": "华东地区生产中心",
    "location": "江苏省苏州市",
    "phone": "0512-88888888",
    "manager": "李四",
    "manager_email": "lisi@company.com",
    "description": "主要负责华东地区的生产和维护",
    "is_active": true,
    "created_at": "2025-01-01T08:00:00Z",
    "updated_at": "2025-12-07T09:00:00Z",
    "user_count": 5,
    "parts_count": 45
  }
}
```

**说明**:
- 可选返回该场站下的用户数和备件数
- 前端暂未使用（预留）

---

## 5. 库存日志模块 (Inventory Logs)

### 5.1 记录库存变化

**请求**:
```
POST /api/inventory-logs
Authorization: Bearer <token>
Content-Type: application/json

{
  "partId": "p-001",
  "operation": "in",
  "qty_before": 8,
  "qty_after": 10,
  "qty_change": 2,
  "reason": "采购入库",
  "notes": "采购订单号: PO-2025-12-001"
}
```

**请求体字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `partId` | string | ✅ | 备件 ID |
| `operation` | string | ✅ | 操作类型：create, update, in, out, adjust |
| `qty_before` | number | ❌ | 变更前数量 |
| `qty_after` | number | ✅ | 变更后数量 |
| `qty_change` | number | ✅ | 变更数量（可为负） |
| `reason` | string | ✅ | 变更原因 |
| `notes` | string | ❌ | 备注信息 |

**响应 (201)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "log-001",
    "partId": "p-001",
    "operation": "in",
    "qty_before": 8,
    "qty_after": 10,
    "qty_change": 2,
    "reason": "采购入库",
    "operator_id": "u1",
    "notes": "采购订单号: PO-2025-12-001",
    "created_at": "2025-12-07T10:00:00Z"
  }
}
```

**说明**:
- 当用户编辑备件时，如果数量改变，应自动记录日志
- 或提供手动记录库存变化的功能（前端未实现）
- 自动记录 `operator_id` = 当前用户 ID

---

### 5.2 查询库存变化日志

**请求**:
```
GET /api/inventory-logs?partId=p-001&page=1&limit=50&days=30
Authorization: Bearer <token>
```

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `partId` | string | ✅ | 备件 ID，查询该备件的日志 |
| `page` | number | ❌ | 页码，默认 1 |
| `limit` | number | ❌ | 每页数量，默认 50 |
| `days` | number | ❌ | 最近 N 天的记录，不指定则所有 |
| `operation` | string | ❌ | 过滤操作类型 |

**响应 (200)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 15,
    "page": 1,
    "limit": 50,
    "items": [
      {
        "id": "log-001",
        "partId": "p-001",
        "operation": "in",
        "qty_before": 8,
        "qty_after": 10,
        "qty_change": 2,
        "reason": "采购入库",
        "operator_id": "u1",
        "operator_name": "张三",
        "notes": "采购订单号: PO-2025-12-001",
        "created_at": "2025-12-07T10:00:00Z"
      },
      ...
    ]
  }
}
```

**说明**:
- 前端暂未实现库存日志查看页面（预留功能）
- 可用于后期的审计日志和数据分析

---

## 6. 错误处理规范

### 统一错误响应格式

所有 API 错误都应返回以下格式：

```json
{
  "code": <错误代码>,
  "message": "<错误描述>",
  "data": null
}
```

### 常见错误代码

| 代码 | HTTP 状态 | 说明 | 场景 |
|------|----------|------|------|
| 0 | 200 | 成功 | 正常响应 |
| 400 | 400 | 请求参数错误 | 字段验证失败、缺少必填字段 |
| 401 | 401 | 未授权 | token 无效、过期、未登录 |
| 403 | 403 | 禁止访问 | 权限不足（编辑非本场站备件等） |
| 404 | 404 | 资源不存在 | 备件/用户/场站不存在 |
| 409 | 409 | 冲突 | 邮箱已存在等唯一性冲突 |
| 500 | 500 | 服务器错误 | 未预期的错误 |

### 错误响应示例

**验证失败**:
```json
{
  "code": 400,
  "message": "验证失败",
  "errors": {
    "name": "备件名称不能为空",
    "qty": "数量必须为非负整数"
  }
}
```

**权限错误**:
```json
{
  "code": 403,
  "message": "无权限编辑此备件（仅限本场站编辑）"
}
```

**认证错误**:
```json
{
  "code": 401,
  "message": "token 无效或已过期，请重新登录"
}
```

---

## 7. 认证与授权

### Token 方案

- **类型**: JWT (JSON Web Token)
- **传递方式**: HTTP Authorization Header
- **格式**: `Authorization: Bearer <token>`

### 示例请求

```
GET /api/parts?stationId=st-001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1MSIsImVtYWlsIjoiemhhbmdzYW5AY29tcGFueS5jb20iLCJzdGF0aW9uSWQiOiJzdC0wMDEiLCJleHAiOjE3MzMwNjMwMDB9.xxx
```

### Token 内容

JWT payload 应包含：

```json
{
  "userId": "u1",
  "email": "zhangsan@company.com",
  "stationId": "st-001",
  "role": "user",
  "exp": 1733063000
}
```

### 过期处理

- **有效期**: 建议 24 小时
- **刷新**: 可选实现刷新令牌机制
- **过期响应**: 返回 401，前端跳转到登录页

---

## 8. 请求/响应说明

### 所有请求都需要

1. **Authorization Header**:
   ```
   Authorization: Bearer <token>
   ```

2. **Content-Type**:
   - GET 请求: `application/x-www-form-urlencoded`
   - POST/PUT 请求: `application/json`

### 所有响应都遵循

1. **HTTP 状态码**: 准确反映请求结果
2. **响应体格式**: 始终使用统一的 JSON 格式
3. **字段类型**: 按规范返回正确的数据类型

### 分页响应

分页接口统一返回以下格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 105,
    "page": 1,
    "limit": 20,
    "items": [...]
  }
}
```

---

## 9. 前端调用流程

### 初始化流程

```
1. 用户打开应用
   ↓
2. 检查 localStorage 中是否有 token
   ├─ 有 token: 跳到步骤 3
   └─ 无 token: 显示登录页，跳到步骤 5
   ↓
3. 调用 GET /api/auth/me 验证 token
   ├─ 成功 (200): 获取用户信息，进入首页
   └─ 失败 (401): token 过期，清除 localStorage，显示登录页
   ↓
4. 首页加载：调用 GET /api/stations 获取场站列表
   ↓
5. 用户输入邮箱密码，调用 POST /api/auth/login
   ├─ 成功 (200): 保存 token，跳到步骤 3
   └─ 失败 (401): 显示错误提示
```

### 列表页流程

```
1. 用户访问 /parts
   ↓
2. 调用 GET /api/parts?stationId=st-001&page=1&limit=20
   ↓
3. 显示备件列表（20 条/页）
   ↓
4. 用户搜索：调用 GET /api/parts?stationId=st-001&search=滤芯
   ↓
5. 用户切换场站：调用 GET /api/parts?stationId=st-002
```

### 详情页流程

```
1. 用户点击某备件的"详情"
   ↓
2. 调用 GET /api/parts/:id
   ↓
3. 显示完整备件信息（含图片）
```

### 编辑页流程

```
1. 编辑模式：加载现有备件
   ├─ 调用 GET /api/parts/:id
   └─ 预填表单
   ↓
2. 创建模式：显示空表单
   ↓
3. 用户填写表单，点击提交
   ├─ 创建: 调用 POST /api/parts
   └─ 编辑: 调用 PUT /api/parts/:id
   ↓
4. 成功后返回列表页
```

---

## 10. 实施建议

### Phase 1: MVP (1-2 周)

必须实现:
- ✅ POST /api/auth/login
- ✅ GET /api/auth/me
- ✅ GET /api/parts (分页)
- ✅ GET /api/parts/:id
- ✅ POST /api/parts
- ✅ PUT /api/parts/:id
- ✅ GET /api/stations

### Phase 2: 完整功能 (第 3 周)

增加:
- ✅ DELETE /api/parts/:id
- ✅ POST /api/inventory-logs
- ✅ GET /api/inventory-logs

### Phase 3: 优化 (第 4 周+)

可选:
- ⚠️ 图片上传到独立服务器/CDN
- ⚠️ 全文搜索优化 (Elasticsearch)
- ⚠️ 用户管理 API
- ⚠️ 权限管理系统

---

## 11. 开发框架建议

### Node.js 生态

```bash
# 推荐框架
npm install express dotenv jwt-simple bcryptjs

# ORM
npm install sequelize mysql2  # 或 typeorm

# 中间件
npm install cors helmet morgan
```

### 最小化 Express 后端示例

```javascript
const express = require('express')
const jwt = require('jwt-simple')
const bcrypt = require('bcryptjs')
const app = express()

app.use(express.json())

// 认证中间件
const auth = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1]
  if (!token) return res.status(401).json({ code: 401, message: 'token 无效' })
  try {
    req.user = jwt.decode(token, 'secret-key')
    next()
  } catch {
    res.status(401).json({ code: 401, message: 'token 已过期' })
  }
}

// 登录
app.post('/api/auth/login', (req, res) => {
  // 验证邮箱密码 → 生成 token
  const token = jwt.encode(
    { userId: 'u1', email: 'test@test.com', stationId: 'st-001', exp: Date.now() + 86400000 },
    'secret-key'
  )
  res.json({ code: 0, message: 'success', data: { token, user: {...} } })
})

// 获取当前用户
app.get('/api/auth/me', auth, (req, res) => {
  res.json({ code: 0, message: 'success', data: req.user })
})

// 获取备件列表
app.get('/api/parts', auth, (req, res) => {
  const { stationId, page = 1, limit = 20, search } = req.query
  // 查询数据库...
  res.json({ code: 0, message: 'success', data: { total: 100, page, limit, items: [] } })
})

app.listen(3000, () => console.log('Server running on port 3000'))
```

### 数据库连接

```javascript
const Sequelize = require('sequelize')
const sequelize = new Sequelize('database', 'user', 'password', {
  host: 'localhost',
  dialect: 'mysql'
})

// 定义模型...
const User = sequelize.define('User', {
  id: { type: Sequelize.UUID, primaryKey: true },
  email: { type: Sequelize.STRING, unique: true },
  password: { type: Sequelize.STRING },
  stationId: { type: Sequelize.UUID, references: { model: 'Station' } }
})
```

---

## 12. API 清单 (快速参考)

| 模块 | 方法 | 路径 | 功能 |
|------|------|------|------|
| **Auth** | POST | /api/auth/login | 用户登录 |
|  | GET | /api/auth/me | 获取当前用户 |
| **Parts** | GET | /api/parts | 列表（分页、搜索、过滤） |
|  | GET | /api/parts/:id | 详情 |
|  | POST | /api/parts | 创建 |
|  | PUT | /api/parts/:id | 更新 |
|  | DELETE | /api/parts/:id | 删除 |
| **Stations** | GET | /api/stations | 列表 |
|  | GET | /api/stations/:id | 详情 |
| **Logs** | POST | /api/inventory-logs | 记录日志 |
|  | GET | /api/inventory-logs | 查询日志 |

---

## 总结

后端需要实现 **11 个 API 端点**，核心是：
1. ✅ 认证与授权 (2 个)
2. ✅ 备件 CRUD (5 个)
3. ✅ 场站查询 (2 个)
4. ✅ 库存日志 (2 个)

**关键安全点**：
- 所有请求都需要 JWT 认证
- 编辑/删除备件必须验证 `user.stationId == part.stationId`
- 返回的所有响应都按统一格式

建议按 Phase 1 → Phase 2 → Phase 3 循序渐进实施！

