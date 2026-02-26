import { computed, watch, ref } from 'vue';
import { useMeta } from 'quasar';
import { usePaperDataStore } from 'src/stores/paperDataStore';

const BASE_URL = 'https://vispubs.com';
const DEFAULT_TITLE = 'Visualization Publications';
const DEFAULT_DESCRIPTION =
  'Repository of visualization publications from VIS, EuroVis, and CHI.';

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export function useSeo() {
  const paperDataStore = usePaperDataStore();

  const jsonLdScript = ref('');

  watch(
    () => paperDataStore.selectedPaper,
    (paper) => {
      if (!paper) {
        jsonLdScript.value = '';
        return;
      }
      const authors = paperDataStore
        .getAuthors(paper)
        .map((a) => ({ '@type': 'Person', name: a.displayName }));

      const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'ScholarlyArticle',
        name: paper.title,
        headline: paper.title,
        abstract: paper.abstract,
        author: authors,
        datePublished: String(paper.year),
        identifier: {
          '@type': 'PropertyValue',
          propertyID: 'DOI',
          value: paper.doi,
        },
        url: `${BASE_URL}/?paper=${encodeURIComponent(paper.doi)}`,
      };
      jsonLdScript.value = JSON.stringify(jsonLd);
    },
    { immediate: true }
  );

  const metaData = computed(() => {
    const paper = paperDataStore.selectedPaper;

    if (!paper) {
      return {
        title: DEFAULT_TITLE,
        meta: {
          description: {
            name: 'description',
            content: DEFAULT_DESCRIPTION,
          },
          ogTitle: { property: 'og:title', content: DEFAULT_TITLE },
          ogDescription: {
            property: 'og:description',
            content: DEFAULT_DESCRIPTION,
          },
          ogUrl: { property: 'og:url', content: BASE_URL },
          ogType: { property: 'og:type', content: 'website' },
        },
        link: {
          canonical: { rel: 'canonical', href: BASE_URL + '/' },
        },
        script: {
          ldJson: jsonLdScript.value
            ? {
                type: 'application/ld+json',
                innerHTML: jsonLdScript.value,
              }
            : undefined,
        },
      };
    }

    const title = `${paper.title} - VisPubs`;
    const description = truncate(paper.abstract || DEFAULT_DESCRIPTION, 155);
    const url = `${BASE_URL}/?paper=${encodeURIComponent(paper.doi)}`;

    return {
      title,
      meta: {
        description: { name: 'description', content: description },
        ogTitle: { property: 'og:title', content: paper.title },
        ogDescription: { property: 'og:description', content: description },
        ogUrl: { property: 'og:url', content: url },
        ogType: { property: 'og:type', content: 'article' },
      },
      link: {
        canonical: { rel: 'canonical', href: url },
      },
      script: {
        ldJson: jsonLdScript.value
          ? {
              type: 'application/ld+json',
              innerHTML: jsonLdScript.value,
            }
          : undefined,
      },
    };
  });

  useMeta(() => metaData.value);
}
