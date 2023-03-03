#! /bin/bash

# reference: https://svelte.dev/docs
npm install pnpm@7.28.0
pnpm create svelte@latest scann_front
cd scann_front
pnpm install
cd ..
cp src/+page.svelte scann_front/src/routes/
