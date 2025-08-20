" Project-specific Neovim configuration for mcp-system-complete
" This file helps LazyVim recognize this directory as a project

" Set project-specific options
set number
set relativenumber
set tabstop=4
set shiftwidth=4
set expandtab

" Python-specific settings
autocmd FileType python setlocal colorcolumn=88
autocmd FileType python setlocal textwidth=87

" Project root markers
let g:projectionist_heuristics = {
      \ "pyproject.toml": {
      \   "*.py": {"type": "source"},
      \   "tests/*.py": {"type": "test"}
      \ }
      \}