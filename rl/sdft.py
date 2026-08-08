"""Backward-compatible launcher for SlideGen completion-only SFT + base KL."""
from __future__ import annotations
import os,sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

def main():
    from rl.sft.sft_toolcall import main as sft_main
    sft_main()

if __name__=="__main__":main()
