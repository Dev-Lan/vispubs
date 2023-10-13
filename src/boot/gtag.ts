import { boot } from 'quasar/wrappers';
import VueGtag from 'vue-gtag';

// "async" is optional;
// more info on params: https://v2.quasar.dev/quasar-cli/boot-files
export default boot(async ({ app, router }) => {
  // something to do
  app.use(
    VueGtag,
    {
      config: { id: 'G-R7TJVFWNR7' },
    },
    router
  );
});
