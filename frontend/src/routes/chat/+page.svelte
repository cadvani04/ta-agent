<script lang="ts">
	import { enhance } from '$app/forms'
	import { Button } from '@/components/ui/button'
	import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
	import { Input } from '@/components/ui/input'
	import { ScrollArea } from '@/components/ui/scroll-area'
	import { Select, SelectContent, SelectItem, SelectTrigger } from '@/components/ui/select'
	import { Loader, Send } from 'lucide-svelte'
	import Markdown from 'svelte-exmarkdown'
	import { gfmPlugin } from 'svelte-exmarkdown/gfm'
	import { Convo } from './Convo.svelte.js'
	import type { SelectCourse } from '@/server/db/auth-schema'
	import { prompt_creation } from '@/utils'

	const plugins = [gfmPlugin()]

	let { data, form } = $props()
	$inspect('data...', data)

	let newMessage = $state('')
	let selectedCourse: SelectCourse | undefined = $state()

	let coursesMap = data.courses.reduce(
		(acc: Record<string, SelectCourse>, course: SelectCourse) => {
			acc[course.courseName] = course
			return acc
		},
		{}
	)

	// {
	//   canvasId: '11883045',
	//   courseName: 'MATH 19B Calculus II',
	//   discordId: '1365763509006372927',
	//   discordChannelId: '1365763511040610365',
	//   userId: 'hqNTL7J929NXirC0FuHcqG5aD7HFSnkF'
	// }
	let isLoading = $state(false)

	let bottomDiv = $state<HTMLDivElement | null>(null)
	let formEl = $state<HTMLFormElement | null>(null)
	let isHistory = $state(true)

	// const triggerContent = $derived(
	// 	data.courses.find((course: any) => course.courseName === selectedCourse.courseName) ??
	// 		'Select a class'
	// )

	const convo = new Convo()

	$effect(() => {
		if (convo.messages.length > 0) {
			bottomDiv?.scrollIntoView({ behavior: 'smooth' })
		}
	})
</script>

{#if !isHistory}
	history
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 pb-52"
	>
		<Select
			type="single"
			onValueChange={(v: string) => {
				selectedCourse = coursesMap[v]
			}}
		>
			<SelectTrigger class="w-[280px]">
				{'Select a class'}
			</SelectTrigger>
			<SelectContent>
				{#each data.courses as cls}
					<SelectItem value={cls.courseName}>{
						cls.courseName
					}</SelectItem>
				{/each}
			</SelectContent>
		</Select>
	</div>
{:else}
	{#if selectedCourse}
		<Card
			class="mx-auto my-5 flex h-[600px] w-full max-w-md flex-col md:max-w-2xl"
		>
			<CardHeader>
				<CardTitle>{selectedCourse.courseName}</CardTitle>
			</CardHeader>
			<CardContent class="flex-1 overflow-hidden">
				<ScrollArea class="h-full p-2">
					{#each convo.messages as msg}
						<div
							class="mb-2 flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}"
						>
							<span
								class="
									max-w-xs break-words rounded-lg px-3 py-2 {msg.role === 'user'
									? 'bg-primary text-primary-foreground'
									: 'bg-secondary text-secondary-foreground'}
								"
							>
								<Markdown md={msg.content} {plugins} />
							</span>
						</div>
					{/each}
					<div bind:this={bottomDiv}></div>
				</ScrollArea>
			</CardContent>
			<CardFooter>
				<form
					action="?/query"
					use:enhance={() => {
						isLoading = true

						convo.addMsg({
							content: newMessage,
							role: 'user',
							userId: selectedCourse?.userId ?? ''
						})

						// newMessage = convo.flattenMsgs() + newMessage
						// console.log('newMessage', newMessage)

						return async ({ update }) => {
							await update()
							if (form) {
								convo.addMsg({
									content: form.response,
									role: 'agent',
									userId: ''
								})
								newMessage = ''
							}
							isLoading = false
							document.getElementById('chat-input')?.focus()
						}
					}}
					method="post"
					class="flex w-full items-center space-x-2"
					bind:this={formEl}
				>
					<Input
						autofocus
						placeholder="Ask a question..."
						bind:value={newMessage}
						onkeydown={(e) => {
							// only plain Enter, not Shift+Enter, and only when not already loading
							if (
								e.key === 'Enter' && !e.shiftKey
								&& !isLoading
							) {
								e.preventDefault()
								formEl?.requestSubmit()
							}
						}}
						name="message"
						class="flex-1"
						autocomplete="off"
						disabled={isLoading}
						id="chat-input"
					/>

					<Button type="submit" disabled={isLoading}>
						{#if isLoading}
							<Loader class="size-4 animate-spin" />
						{:else}
							<Send />
						{/if}
					</Button>

					{#if true}
						{@const sc = selectedCourse}
						<input
							type="hidden"
							name="prompt"
							value={prompt_creation(
								sc.courseName,
								sc.canvasId,
								sc.discordChannelId ?? '',
								sc.discordId ?? '',
								sc.slackName ?? ''
							)}
						/>
					{/if}
					<input
						type="hidden"
						name="context"
						value={convo.flattenMsgs()}
					/>
					<input
						type="hidden"
						name="convoId"
						value={convo.convoId()}
					/>
				</form>
			</CardFooter>
		</Card>
	{:else}
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 pb-52"
		>
			<Select
				type="single"
				onValueChange={(v: string) => {
					selectedCourse = coursesMap[v]
				}}
			>
				<SelectTrigger class="w-[280px]">
					{'Select a class'}
				</SelectTrigger>
				<SelectContent>
					{#each data.courses as cls}
						<SelectItem value={cls.courseName}>{
							cls.courseName
						}</SelectItem>
					{/each}
				</SelectContent>
			</Select>
		</div>
	{/if}
{/if}
