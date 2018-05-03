#!/bin/bash
echo "creating final words for GS"
python create_final_words.py GS
echo "week 1..."
python preprocess_data.py GS 1
echo "week 2.."
python preprocess_data.py GS 2
echo "week 3.."
python preprocess_data.py GS 3
echo "creating final words for HD"
python create_final_words.py HD
echo "week 1..."
python preprocess_data.py HD 1
echo "week 2.."
python preprocess_data.py HD 2
echo "week 3.."
python preprocess_data.py HD 3
echo "creating final words for IBM"
python create_final_words.py IBM
echo "week 1.."
python preprocess_data.py IBM 1
echo "week 2.."
python preprocess_data.py IBM 2
echo "week 3.."
python preprocess_data.py IBM 3
echo "creating final words for INTC"
python create_final_words.py INTC
echo "week 1.."
python preprocess_data.py INTC 1
echo "week 2.."
python preprocess_data.py INTC 2
echo "week 3.."
python preprocess_data.py INTC 3
