" citerius.vim
" Maintainer: Vasissualiyp
" Version: 0.1

function! citerius#InitPaths()
    let default_references_path = '~/research/references'
	let default_citerius_github_integration = 0

	" Set default values
	let g:citerius_references_dir = exists('g:citerius_references_dir') ? g:citerius_references_dir : default_references_path
	let g:citerius_github_integration = exists('g:citerius_github_integration') ? g:citerius_github_integration : default_citerius_github_integration

endfunction

let g:citerius_source_dir = expand('<sfile>:p:h') . '/..'

"command! CiteriusCleanup call citerius#CiteriusCleanup()
"command! CiteriusGitPush call citerius#CiteriusGitPush()
"command! SetupCiteriusReferences call citerius#SetupCiteriusReferences()
"command! DisplayCiteriusQuickhelp call citerius#DisplayCiteriusQuickhelp()
"command! CiteriusGitPull call citerius#CiteriusSyncWithRemoteRepo(expand(g:citerius_notes_dir))
