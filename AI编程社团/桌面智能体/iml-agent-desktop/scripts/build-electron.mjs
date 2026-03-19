import * as esbuild from 'esbuild';

await esbuild.build({
  entryPoints: ['electron/main.ts', 'electron/preload.ts'],
  bundle: true,
  platform: 'node',
  target: 'node18',
  outdir: 'dist-electron',
  outExtension: { '.js': '.cjs' },
  external: ['electron', 'electron-squirrel-startup', 'electron-store'],
  format: 'cjs',
  sourcemap: true,
});
