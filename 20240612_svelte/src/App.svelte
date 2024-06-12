<script>
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
  import Counter from './lib/Counter.svelte'


  import { supabase } from './lib/supabaseClient';
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

<main>
  <div>
    <a href="https://vitejs.dev" target="_blank" rel="noreferrer">
      <img src={viteLogo} class="logo" alt="Vite Logo" />
    </a>
    <a href="https://svelte.dev" target="_blank" rel="noreferrer">
      <img src={svelteLogo} class="logo svelte" alt="Svelte Logo" />
    </a>
  </div>
  <h1>Vite + Svelte</h1>

  <div class="card">
    <Counter />
  </div>

  <p>
    Check out <a href="https://github.com/sveltejs/kit#readme" target="_blank" rel="noreferrer">SvelteKit</a>, the official Svelte app framework powered by Vite!
  </p>

  <p class="read-the-docs">
    Click on the Vite and Svelte logos to learn more
  </p>
  <h1 class="text-3xl font-bold hover:underline">
    Hello world!
  </h1>

  <div class="signin-container">
    {#if user}
        <img style="width: 100px; height: auto;" src={user.user_metadata.avatar_url} alt="avatar" />
        <button on:click={signOut}>Sign out</button>
    {:else}
        <button on:click={signInWithGithub}>Sign in with GitHub</button>
    {/if}
  </div>
</main>

<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  }
  .signin-container {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 30vh;
  }
</style>
