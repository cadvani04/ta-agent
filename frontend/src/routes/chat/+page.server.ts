import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ request, fetch }) => {

  const res = await fetch('/api/basic');

  console.log('res', res)

  if (!res.ok) {
    throw new Error(`Fetch failed: ${res.status}`);
  }

  const data = await res.json();
  return { data }
}
