import { ref, watch } from 'vue';
import { defineStore } from 'pinia';
import { useQuasar } from 'quasar';

export const useGlobalStore = defineStore('globalStore', () => {
  const $q = useQuasar();
  const darkMode = ref<boolean>(sessionStorage.getItem('darkMode') !== 'false');

  $q.dark.set(!darkMode.value);

  watch(darkMode, (value) => {
    sessionStorage.setItem('darkMode', value.toString());
    $q.dark.set(!darkMode.value);
  });
  return { darkMode };
});
