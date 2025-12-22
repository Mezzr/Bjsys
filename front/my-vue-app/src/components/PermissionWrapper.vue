<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '../stores/user'

const props = defineProps<{ stationId?: string }>()
const userStore = useUserStore()

const canEdit = computed(() => {
  if (!props.stationId) return false
  const user = userStore.user
  if (!user) return false
  if (user.can_manage_users) return true
  if (!user.site || !user.can_edit_own_site) return false
  return user.site === props.stationId
})
</script>

<template>
  <div>
    <slot v-if="canEdit"></slot>
    <slot v-else name="no-permission"></slot>
  </div>
</template>
