<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="bg-primary text-white" height-hint="98">
      <q-toolbar>
        <q-tabs align="left">
          <q-route-tab to="/" label="Vis Publications" />
          <q-route-tab to="/about" label="About" />
        </q-tabs>
      </q-toolbar>
    </q-header>
    <router-view />
  </q-layout>
</template>

<script setup lang="ts"></script>
