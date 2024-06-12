<script>
    import { supabase } from '$lib/supabaseClient';
    import { onMount } from 'svelte';

    let user;

    onMount(async () => {
        user = await currentUser();
    });

    async function currentUser() {
        const { data } = await supabase.auth.getUser();
        return data.user;
    }

    async function signInWithGithub() {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'github'
        });
    }

    async function signOut() {
        const { error } = await supabase.auth.signOut();
        user = null;
    }
</script>

<div class="signin-container">
    {#if user}
        <img style="width: 100px; height: auto;" src={user.user_metadata.avatar_url} alt="avatar" />
        <button on:click={signOut}>Sign out</button>
    {:else}
        <button on:click={signInWithGithub}>Sign in with GitHub</button>
    {/if}
</div>

<style>
    .signin-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
</style>
