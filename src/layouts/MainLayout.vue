<script setup lang="ts">
import { useGlobalStore } from 'src/stores/globalStore';
const globalStore = useGlobalStore();
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="bg-primary text-white" height-hint="98">
      <q-toolbar>
        <q-tabs inline-label align="left">
          <q-route-tab to="/" label="Vis Publications" icon="img:logo.svg" />
          <q-route-tab to="/about" label="About" />
        </q-tabs>
        <q-space></q-space>
        <q-toggle
          v-model="globalStore.darkMode"
          checked-icon="light_mode"
          color="yellow-8"
          unchecked-icon="dark_mode"
          :title="`Switch to ${globalStore.darkMode ? 'dark' : 'light'} mode`"
        />
        <q-btn
          href="https://github.com/Dev-Lan/vispubs"
          target="_blank"
          flat
          round
          size="md"
          icon="fa-brands fa-github"
        />
      </q-toolbar>
    </q-header>
    <router-view />
  </q-layout>
</template>
