if [[ $OSTYPE == darwin* ]]; then
    # Mac OSX
    brew update && brew install sox
elif [[ $OSTYPE == linux-gnu ]]; then
    # GNU/Linux
    apt-get update && apt-get install -y sox
fi
pip install --upgrade --force-reinstall --pre torchaudio --index-url https://download.pytorch.org/whl/nightly
pip install -r requirements.txt
