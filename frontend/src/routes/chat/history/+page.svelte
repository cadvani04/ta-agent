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
    import Convo from './Convo.svelte.js'
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

    let isLoading = $state(false)

    let bottomDiv = $state<HTMLDivElement | null>(null)
    let formEl = $state<HTMLFormElement | null>(null)
    let isHistory = $state(true)

    const triggerContent = $derived(
        data.courses.find((course: any) => course.courseName === selectedCourse.courseName) ??
            'Select a class'
    )

    const convo = new Convo()

    $effect(() => {
        if (convo.messages.length > 0) {
            bottomDiv?.scrollIntoView({ behavior: 'smooth' })
        }
    })
</script>