<script>
  import Router from 'svelte-spa-router';
  import routes from "./routes";

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
  <a href="/">홈</a>
  <a href="/#/About">어바웃</a>
  <!-- <div>
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
  </h1> -->

  <!-- <div class="signin-container">
    {#if user}
        <img style="width: 100px; height: auto;" src={user.user_metadata.avatar_url} alt="avatar" />
        <button on:click={signOut}>Sign out</button>
    {:else}
        <button on:click={signInWithGithub}>Sign in with GitHub</button>
    {/if}
  </div> -->
  <!-- This example requires Tailwind CSS v2.0+ -->
  <div class="bg-gray-50">
    <div
      class="mx-auto max-w-7xl py-12 px-4 sm:px-6 lg:flex lg:items-center lg:justify-between lg:py-16 lg:px-8"
    >
      <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        <span class="block">Ready to dive in?</span>
        <span class="block text-indigo-600">Start your free trial today.</span>
      </h2>
      <div class="mt-8 flex lg:mt-0 lg:flex-shrink-0">
        <div class="inline-flex rounded-md shadow">
          <a
            href="#"
            class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-5 py-3 text-base font-medium text-white hover:bg-indigo-700"
            >Get started</a
          >
        </div>
        <div class="ml-3 inline-flex rounded-md shadow">
          <a
            href="#"
            class="inline-flex items-center justify-center rounded-md border border-transparent bg-white px-5 py-3 text-base font-medium text-indigo-600 hover:bg-indigo-50"
            >Learn more</a
          >
        </div>
      </div>
    </div>
  </div>
</main>

<Router {routes}/>
<!-- <Router
  routes={{
    "/": Home,
    "/about": About,
  }}
/> -->

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
