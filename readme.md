## enviromon

It's an environment monitoring component.

### What it do

Tells me the temperature very very precisely.

### How to use

I'm running a Raspberry Pi 3 Model B with an MCP3008 as the analog-digital-converter (ADC).

Either run the code as root or create a world read/writeable device for the SPI port.

I don't imagine a hardware analog sensor is going to own you, even so, bad practise is bad practise.

```
git clone https://github.com/dbrownidau/enviromon.git
cd ./enviromon
python -m venv .enviromon
source .enviromon/bin/activate
pip install -r requirements.txt
chmod +x enviromon.py
./enviromon.py
```
