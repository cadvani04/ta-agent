<script lang="ts">
	import { Button } from '@/components/ui/button'
	import type { User } from 'better-auth'

	const { data }: { data: { user: User | null } } = $props()
	$inspect(data)
</script>

Welcome to TA Agent.
