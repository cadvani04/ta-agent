<script lang="ts">
	import '../app.css'
	import { Button } from '@/components/ui/button'
	import type { Snippet } from 'svelte'
	import { logIn, logOut } from '@/auth-client'
	import { History, SquarePen } from 'lucide-svelte'

	const { children, data }: {
		data: { user: import('better-auth').User | null }
		children: Snippet
	} = $props()
</script>

<nav class="flex items-center justify-between p-4">
	<ul class="flex space-x-2">
		<li>
			<Button variant="outline" href="/chat"><History /></Button>
		</li>
		<li>
			<Button variant="outline" href="/chat"><SquarePen /></Button>
		</li>
	</ul>

	{#if data?.user}
		<div>
			<Button onclick={logOut}>Logout</Button>
		</div>
	{:else}
		<Button onclick={logIn}>Login</Button>
	{/if}
</nav>

{@render children()}
