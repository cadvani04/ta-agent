<script lang="ts">
	import { Button } from '@/components/ui/button'
	import { signIn, signOut } from '@/auth/login'

	const { data }: { data: { user: import('better-auth').User | null } } = $props()
</script>

{#if data?.user}
	<div>
		<p>
			{data.user.email}
		</p>
		<Button onclick={signOut}>Signout</Button>
	</div>
{:else}
	<Button onclick={signIn}>Continue with google</Button>
{/if}
