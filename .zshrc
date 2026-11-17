export ZSH="${HOME}/.oh-my-zsh"

# theme
ZSH_THEME="linuxonly"

# aliases
source $ZSH/oh-my-zsh.sh
source $HOME/.aliases

# Ona secrets
[ -f /etc/profile.d/ona-secrets.sh ] && . /etc/profile.d/ona-secrets.sh
[ -f "$HOME/.agent-setup/shell/agents.sh" ] && . "$HOME/.agent-setup/shell/agents.sh"
