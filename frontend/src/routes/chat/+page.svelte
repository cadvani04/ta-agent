<script lang="ts">
	import { Button } from '@/components/ui/button'
	import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
	import { Input } from '@/components/ui/input'
	import { ScrollArea } from '@/components/ui/scroll-area'
	import { Select, SelectContent, SelectItem, SelectTrigger } from '@/components/ui/select'
	import { Loader, Send } from 'lucide-svelte'

	let { data } = $props()
	$inspect('data...', data)

	interface Message {
		id: number
		content: string
		sender: 'user' | 'bot'
	}

	let classes = $state([
		'Intro to CS',
		'Discrete Math',
		'Data Structures',
		'Comp Arch',
		'Operating Sys',
		'Databases',
		'Networks',
		'Software Eng',
		'ML'
	])

	let messages: Message[] = $state([])
	let newMessage = $state('')
	let selectedClass = $state('')
	let isLoading = $state(false)

	// svelte-ignore non_reactive_update
	let bottomDiv: HTMLDivElement

	$inspect(selectedClass, 'selectedClass')

	const triggerContent = $derived(
		classes.find((cls) => cls === selectedClass) ?? 'Select a class'
	)

	function sendMessage() {
		isLoading = true

		if (newMessage.trim()) {
			messages = [...messages, {
				id: Date.now(),
				content: newMessage,
				sender: 'user'
			}]
			newMessage = ''
			// simulate bot response
			setTimeout(() => {
				messages = [...messages, {
					id: Date.now() + 1,
					content: 'This is a response from the bot',
					sender: 'bot'
				}]
				isLoading = false
			}, 1000)
		}
	}

	// Scroll to the bottom whenever messages update
	$effect(() => {
		if (messages.length > 0) {
			bottomDiv.scrollIntoView({ behavior: 'smooth' })
		}
	})
</script>

{#if selectedClass}
	<Card
		class="mx-auto my-5 flex h-[600px] w-full max-w-md flex-col md:max-w-2xl"
	>
		<CardHeader>
			<CardTitle>{selectedClass}</CardTitle>
		</CardHeader>
		<CardContent class="flex-1 overflow-hidden">
			<ScrollArea class="h-full p-2">
				{#each messages as msg (msg.id)}
					<div
						class="mb-2 flex {msg.sender === 'user' ? 'justify-end' : 'justify-start'}"
					>
						<span
							class="
								max-w-xs break-words rounded-lg px-3 py-2 {msg.sender === 'user'
								? 'bg-primary text-primary-foreground'
								: 'bg-secondary text-secondary-foreground'}
							"
						>
							{msg.content}
						</span>
					</div>
				{/each}
				<div bind:this={bottomDiv}></div>
			</ScrollArea>
		</CardContent>
		<CardFooter class="flex items-center space-x-2">
			<Input
				placeholder="Ask a question..."
				bind:value={newMessage}
				onkeypress={(e) => !isLoading && e.key === 'Enter' && sendMessage()}
				class="flex-1"
			/>

			<Button onclick={sendMessage} type="submit" disabled={isLoading}>
				{#if isLoading}
					<Loader class="size-4 animate-spin" />
				{:else}
					<Send />
				{/if}
			</Button>
		</CardFooter>
	</Card>
{:else}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 pb-36"
	>
		<Select
			type="single"
			value={selectedClass}
			onValueChange={(v) => {
				selectedClass = v
			}}
		>
			<SelectTrigger class="w-[180px]">
				{triggerContent}
			</SelectTrigger>
			<SelectContent>
				{#each classes as cls}
					<SelectItem value={cls}>{cls}</SelectItem>
				{/each}
			</SelectContent>
		</Select>
	</div>
{/if}
