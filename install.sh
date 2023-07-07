if [[ $OSTYPE == darwin* ]]; then
    # Mac OSX
    brew update && brew install sox
elif [[ $OSTYPE == linux-gnu ]]; then
    # GNU/Linux
    apt-get update && apt-get install -y sox
fi

# check cuda availability
if command -v nvidia-smi &> /dev/null
then
    echo "GPU available: installing GPU version"
    pip install --upgrade --force-reinstall --pre torchaudio --index-url https://download.pytorch.org/whl/nightly/cu118
else
    echo "CPU only: installing CPU version"
    pip install --upgrade --force-reinstall --pre torchaudio --index-url https://download.pytorch.org/whl/nightly
fi

pip install -r requirements.txt
