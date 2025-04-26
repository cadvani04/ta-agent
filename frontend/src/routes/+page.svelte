<script lang="ts">
	import { authClient } from '$lib/client'
	import { Button } from '@/components/ui/button'

	const { data }: { data: { user: import('better-auth').User | null } } = $props()
</script>

{#if data?.user}
	<div>
		<p>
			{data?.user.email}
		</p>
		<Button
			onclick={async () => {
				await authClient.signOut({
					fetchOptions: {
						onSuccess: () => {
							window.location.reload()
						}
					}
				})
			}}
		>
			Signout
		</Button>
	</div>
{:else}
	<Button
		onclick={async () => {
			await authClient.signIn.social({
				provider: 'google'
			})
		}}
	>
		Continue with google
	</Button>
{/if}
