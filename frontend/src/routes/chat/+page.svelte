<script lang="ts">
	import { Button } from '@/components/ui/button'
	import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
	import { Input } from '@/components/ui/input'
	import { ScrollArea } from '@/components/ui/scroll-area'

	interface Message {
		id: number
		content: string
		sender: 'user' | 'bot'
	}

	let messages: Message[] = []
	let newMessage = ''

	function sendMessage() {
		if (newMessage.trim()) {
			messages = [...messages, { id: Date.now(), content: newMessage, sender: 'user' }]
			newMessage = ''
			// simulate bot response
			setTimeout(() => {
				messages = [
					...messages,
					{ id: Date.now() + 1, content: 'This is a response from the bot.', sender: 'bot' }
				]
			}, 1000)
		}
	}
</script>

<Card class="mx-auto mt-8 flex h-[600px] w-full max-w-md flex-col">
	<CardHeader>
		<CardTitle>Chat Interface</CardTitle>
	</CardHeader>
	<CardContent class="flex-1 overflow-hidden">
		<ScrollArea class="h-full p-2">
			{#each messages as msg (msg.id)}
				<div class="mb-2 flex {msg.sender === 'user' ? 'justify-end' : 'justify-start'}">
					<span
						class="max-w-xs break-words rounded-lg px-3 py-2 {msg.sender === 'user'
							? 'bg-primary text-primary-foreground'
							: 'bg-secondary text-secondary-foreground'}"
					>
						{msg.content}
					</span>
				</div>
			{/each}
		</ScrollArea>
	</CardContent>
	<CardFooter class="flex items-center space-x-2">
		<Input
			placeholder="Ask a question..."
			bind:value={newMessage}
			onkeypress={(e) => e.key === 'Enter' && sendMessage()}
			class="flex-1"
		/>

		<Button onclick={sendMessage}>Send</Button>
	</CardFooter>
</Card>
