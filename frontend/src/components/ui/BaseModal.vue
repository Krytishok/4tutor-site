<!-- src/components/ui/BaseModal.vue -->
<script setup lang="ts">
defineProps<{ show: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-backdrop" @click.self="emit('close')">
      <div class="modal-content card">
        <button class="modal-close btn" @click="emit('close')" aria-label="Закрыть">✕</button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  padding: 20px;
}
.modal-content {
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  border-radius: var(--radius-lg);
  padding: 24px;
}
.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  line-height: 1;
  color: var(--muted);
}
</style>