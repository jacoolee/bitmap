#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""ASCII based compound bitmap"""

import math
from bitmap import BitMapAbs, BitMap


class CompoundBitMap(BitMapAbs):
    def __init__(self,
                 convert_2_uniq_digit_str_hook=None,
                 speed_comes_first=False,
                 n_width_raw_per_bitmap=None):
        """
        @convert_2_uniq_digit_str_hook: function for convert
        a raw string into a string with each char is a digit,
        if None, use default

        @speed_comes_first: if true, less but bigger bitmaps
        are created for speed, else, more but smaller bitmaps
        are create for memory saving with slower speed cost.

        CAUTIONS: according to test, if this arg is enabled
        and the raw string is very long, the memory cost is
        very significant.

        @n_width_raw_per_bitmap: provide a way for split raw
        string with specific width manually,
        Still, more probe and testing is preferred for a goods
        chosen value.
        """
        if convert_2_uniq_digit_str_hook:
            assert callable(convert_2_uniq_digit_str_hook), \
                "invalid args:@convert_2_uniq_digit_str_hook should be callable"
        if speed_comes_first:
            assert isinstance(speed_comes_first, bool), \
                "invalid args:@speed_comes_first should be bool"
        if n_width_raw_per_bitmap:
            assert type(n_width_raw_per_bitmap) in (int, long), \
                "invalid args:@n_width_raw_per_bitmap should be 'int' or 'long'"

        self._convert_2_uniq_digit_str_hook \
            = convert_2_uniq_digit_str_hook or self._convert_2_uniq_digit_str
        self._n_width_raw_per_bm \
            = n_width_raw_per_bitmap or 4 if speed_comes_first else 2
        self._bitmaps = []

    def _convert_2_uniq_digit_str(self, raw_str):
        """
        convert raw_str to a string with each item is a digit

        NOTICE: raw2digit_width is needed for
        *EACH RAW CHAR ocupys same WIDTH SPACE represented by digit*

        @return: (digit_str, raw2digit_width)
        """
        return ''.join([str(ord(i)-28) for i in raw_str]) if raw_str else '0', 2

    def _get_oprands(self, raw_str, do_prepare=True):
        """generate compound bitmap dynamically

        @raw_str: raw string
        @N: number of raw chars used to compose a bitmap
        """
        # if exceeds, return immediately
        if not do_prepare and len(self._bitmaps)*self._n_width_raw_per_bm<len(raw_str):
            return []
        digit_str, width = self._convert_2_uniq_digit_str_hook(raw_str)
        return self._split_digit_str(digit_str, width * self._n_width_raw_per_bm)

    def _split_digit_str(self, digit_str, n_digit_per_bitmap):
        """
        split a digit string by @n_digit_per_bitmap digits as a
        group, to create bitmaps if dynamically

        @digit_str: each char in string is represented in digit
        @n_digit_per_bitmap: number of digit chars used to create
        a bitmap.
        @return: [(bm, n_width_digits), ...]

        NOTICE: for performace and easy code: bitmaps has the
        reverse order as the digit_str.
        """
        ret = []
        s, bms_idx = digit_str, -1
        while s:
            n_width_digits = s[-n_digit_per_bitmap:]
            s, bms_idx = s[:-n_digit_per_bitmap], bms_idx + 1
            if bms_idx >= len(self._bitmaps): # not exist
                self._bitmaps.append(BitMap())
            ret.append( (self._bitmaps[bms_idx], n_width_digits) )
        #finally
        return ret

    def turnOn(self, raw_str):
        oprands = self._get_oprands(raw_str)
        for i in oprands:
            i[0].turnOn(long(i[1]))
        return self

    def turnOff(self, raw_str):
        oprands = self._get_oprands(raw_str)
        for i in oprands:
            i[0].turnOff(long(i[1]))
        return self

    def isTurnedOn(self, raw_str):
        oprands = self._get_oprands(raw_str, do_prepare=False)
        if not oprands:
            return False
        ret = 1
        for i in oprands:
            ret &= i[0].isTurnedOn(long(i[1]))
            if not ret:
                return False
        # finally
        return True

    def _probe_mem(self, maxN=10, maxM=100, mtype='KB', N_oriented=True):
        X = (maxN, 'N') if N_oriented else (maxM, 'M')
        Y = (maxM, 'M') if N_oriented else (maxN, 'N')
        for i in xrange(1, X[0]):
            print "_" * 50
            for j in xrange(1, Y[0]):
                m = self._approx_mem_size_in_type(i,j,mtype)
                print "%s:%2s %s:%2s Mem:%s (%2s)" % (X[1],i,Y[1],j,m,mtype)

    def _approx_mem_size_in_type(self, N, M, mtype='KB'):
        """
        NOTICE: just a approx memory size guesser, for the real size, please
        use f:self.info()
        @N: number of raw chars used to compose a bitmap
        @M: length of raw 'S'
        @type: convert to memory size type

        memory size formula:
        mem_MB_size = 2 ** ( log2( 10 ** (N*2)) - MB:23 ) * M/N
        """
        assert N > 0, 'N should be positive'
        assert M > 0, 'M should be positive'
        mtype_bin_exponents = { 'GB': 33,
                                'MB': 23,
                                'KB': 13,
                                'B': 3,
                                'b': 0
        }
        if mtype not in mtype_bin_exponents:
            raise ValueError("unsupported argument:'%s' not in %s" %
                             (mtype, mtype_bin_exponents.keys()))
        return math.pow(2, math.log(( math.pow(10, N*2) ), 2) - mtype_bin_exponents[mtype]) * M/N

    def info(self):
        bit_length = 0
        for i in self._bitmaps:
            bit_length += i.bitLength()

        return dict(
            base_item_type         = BitMap.BASE_ITEM_TYPE,
            base_item_byte_size    = BitMap.BASE_ITEM_BYTE_SIZE,
            base_item_bit_size     = BitMap.BASE_ITEM_BIT_SIZE,
            os_bit_shift           = BitMap.OS_BIT_SHIFT,
            os_bit_mask            = BitMap.OS_BIT_MASK,
            bit_length             = self.bitLength(),
            mem_size_in_kb         = self.bitLength() >> 13,
            bitmap_count           = len(self._bitmaps),
            n_width_raw_per_bitmap = self._n_width_raw_per_bm,
        )

    def bitLength(self):
        bit_length = 0
        for i in self._bitmaps:
            bit_length += i.bitLength()
        return bit_length
