<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePartsStore } from '../stores/parts'
import { useUserStore } from '../stores/user'
import { storeToRefs } from 'pinia'
import { ElMessage, ElForm, ElFormItem, ElInput, ElInputNumber, ElSelect, ElOption, ElButton, ElUpload, ElIcon, ElAlert } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { UploadProps } from 'element-plus'

const partsStore = usePartsStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { categories } = storeToRefs(partsStore)

const isEdit = Boolean(route.params.id)
const formRef = ref()

// 定义表单数据结构，与后端模型保持一致
const form = ref({
  name: '',
  model: 'UNKNOWN', // 默认值
  description: '',
  location: '',
  supplier: '',
  supplier_code: '',
  quantity: 0,
  alarmQty: 5, // 默认值
  procurementDays: 7, // 默认值
  categoryId: undefined as number | undefined,
  siteId: undefined as number | undefined, // 场站ID
  status: 'active', // 默认值
  imageUrl: ''
})
const loading = ref(false)

const rules = {
  name: [{ required: true, message: '请输入备件名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

// 获取当前用户的场站名称（用于显示）
const currentSiteName = computed(() => {
  return userStore.user?.site || '未分配'
})

onMounted(async () => {
  await userStore.fetchMe()
  await partsStore.fetchCategories()
  
  // 如果是新增，自动填充当前用户的场站ID
  if (!isEdit && userStore.user?.site_id) {
    form.value.siteId = userStore.user.site_id
  }

  if (isEdit) {
    const id = route.params.id as string
    const p = await partsStore.getPart(id)
    if (p) {
      form.value = {
        name: p.name,
        model: p.model || 'UNKNOWN',
        description: p.description || '',
        location: p.location || '',
        supplier: p.supplier || '',
        supplier_code: p.supplier_code || '',
        quantity: p.quantity,
        alarmQty: p.alarmQty || 5,
        procurementDays: p.procurementDays || 7,
        categoryId: p.categoryId || p.category?.id,
        siteId: p.stationId ? Number(p.stationId) : undefined, // 映射 stationId 到 siteId
        status: p.status || 'active',
        imageUrl: p.imageUrl || ''
      }
    }
  }
})

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      // 再次检查 siteId
      if (!form.value.siteId && userStore.user?.site_id) {
        form.value.siteId = userStore.user.site_id
      }

      loading.value = true
      try {
        if (isEdit) {
          const id = route.params.id as string
          await partsStore.updatePart(id, form.value)
          ElMessage.success('更新成功')
          router.push({ name: 'PartDetail', params: { id } })
        } else {
          await partsStore.createPart(form.value)
          ElMessage.success('创建成功')
          router.push({ name: 'PartsList' })
        }
      } catch (e: any) {
        console.error(e)
        let msg = '操作失败'
        if (e.response && e.response.data) {
            const data = e.response.data
            if (data.message) {
                msg = data.message
            } else if (typeof data === 'object') {
                // 处理 DRF 字段验证错误 {"field": ["error"]}
                const errors = []
                for (const key in data) {
                    if (Array.isArray(data[key])) {
                        errors.push(`${key}: ${data[key].join(', ')}`)
                    } else {
                        errors.push(`${key}: ${data[key]}`)
                    }
                }
                if (errors.length > 0) msg = errors.join('; ')
            }
        }
        ElMessage.error(msg)
      } finally {
        loading.value = false
      }
    }
  })
}

function goBack() {
  router.back()
}

const handleImageUpload: UploadProps['onChange'] = (file) => {
  if (file.raw) {
    const reader = new FileReader()
    reader.onload = (evt) => {
      form.value.imageUrl = evt.target?.result as string
    }
    reader.readAsDataURL(file.raw)
  }
}
</script>

<template>
  <div class="part-form-container">
    <div class="header">
      <h2>{{ isEdit ? '编辑备件' : '新增备件' }}</h2>
      <div class="site-info" v-if="currentSiteName">
        当前场站: <el-tag>{{ currentSiteName }}</el-tag>
      </div>
    </div>

    <el-alert
      v-if="!form.siteId && !isEdit"
      title="警告：当前用户未关联场站，可能无法创建备件"
      type="warning"
      show-icon
      style="margin-bottom: 20px;"
    />

    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 800px">
      <el-form-item label="备件名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入备件名称" />
      </el-form-item>

      <el-form-item label="备件型号" prop="model">
        <el-input v-model="form.model" placeholder="如 FC-2000 (默认为 UNKNOWN)" />
      </el-form-item>

      <el-form-item label="场站ID" prop="siteId" v-if="!currentSiteName || currentSiteName === '未分配' || userStore.user?.can_view_all_sites">
        <el-input-number v-model="form.siteId" :min="1" style="width: 100%" placeholder="请输入场站ID (MySQL中的ID)" />
        <div style="font-size: 12px; color: #999; line-height: 1.2; margin-top: 4px;">
          通常自动填充。如果当前用户未关联场站，请手动输入目标场站的数据库ID。
        </div>
      </el-form-item>

      <el-form-item label="分类" prop="categoryId">
        <el-select v-model="form.categoryId" placeholder="请选择分类" style="width: 100%">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="存放位置" prop="location">
        <el-input v-model="form.location" placeholder="如 仓库 A - 第2排" />
      </el-form-item>

      <el-form-item label="供应商" prop="supplier">
        <el-input v-model="form.supplier" placeholder="供应商名称" />
      </el-form-item>

      <el-form-item label="供应商编码" prop="supplier_code">
        <el-input v-model="form.supplier_code" placeholder="供应商内部编码" />
      </el-form-item>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px">
        <el-form-item label="当前数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="告警数量" prop="alarmQty">
          <el-input-number v-model="form.alarmQty" :min="0" style="width: 100%" placeholder="库存下限" />
        </el-form-item>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px">
        <el-form-item label="采购周期(天)" prop="procurementDays">
          <el-input-number v-model="form.procurementDays" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="活跃" value="active" />
            <el-option label="停用" value="inactive" />
            <el-option label="已淘汰" value="obsolete" />
          </el-select>
        </el-form-item>
      </div>

      <el-form-item label="备件描述" prop="description">
        <el-input type="textarea" v-model="form.description" :rows="3" placeholder="备件说明、用途等" />
      </el-form-item>

      <el-form-item label="备件图片">
        <el-upload
          class="avatar-uploader"
          action="#"
          :show-file-list="false"
          :auto-upload="false"
          :on-change="handleImageUpload"
        >
          <img v-if="form.imageUrl" :src="form.imageUrl" class="avatar" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
        <el-button @click="goBack">返回</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.part-form-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.site-info {
  font-size: 14px;
  color: #666;
}
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}
.avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style>