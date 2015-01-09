#! /usr/bin/env python
# -*- coding: utf-8 -*-

import array


class BitMapAbs(object):
    """ abstrict Interface for bitmap and compound bit map
    """
    def __init__(self, *args, **kwargs):
        pass

    def turnOn(self, bit_loc):
        raise NotImplemented('turnOn')

    def turnOff(self, bit_loc):
        raise NotImplemented('turnOff')

    def isTurnedOn(self, bit_loc):
        raise NotImplemented('isTurnedOn')

    def clearAll(self):
        raise NotImplemented('clearAll')

    def erase(self):
        raise NotImplemented('erase')

    def bitLength(self):
        raise NotImplemented('bitLength')

    def info(self):
        raise NotImplemented('info')

    def negate(self):
        raise NotImplemented('negate')

    def union(self, bit_map):
        raise NotImplemented('union')

    def intersect(self, bit_map):
        raise NotImplemented('intersect')

    def reset(self, bit_map):
        raise NotImplemented('reset')


class BitMap(BitMapAbs):
    BASE_ITEM_TYPE = 'l'        # signed long, for negate-compatible
    BASE_ITEM_VALUE = 0L

    BASE_ITEM_BYTE_SIZE = array.array(BASE_ITEM_TYPE).itemsize # in byte
    BASE_ITEM_BIT_SIZE = BASE_ITEM_BYTE_SIZE << 3

    OS_BIT_SHIFT =    5 if BASE_ITEM_BYTE_SIZE == 4 else 6    # 32bit or 64bit
    OS_BIT_MASK  = 0x1F if BASE_ITEM_BYTE_SIZE == 4 else 0x3F # 32bit or 64bit

    # "<<" vs "Memory Cache", almost same, and "Memory Cache" is a little bit
    # faster when tons(like, 1,000,000) of index fetching operations are performed.
    BITS = [
        1L <<  0, 1L <<  1, 1L <<  2, 1L <<  3, 1L <<  4, 1L <<  5, 1L <<  6, 1L <<  7,
        1L <<  8, 1L <<  9, 1L << 10, 1L << 11, 1L << 12, 1L << 13, 1L << 14, 1L << 15,
        1L << 16, 1L << 17, 1L << 18, 1L << 19, 1L << 20, 1L << 21, 1L << 22, 1L << 23,
        1L << 24, 1L << 25, 1L << 26, 1L << 27, 1L << 28, 1L << 29, 1L << 30, 1L << 31,
        1L << 32, 1L << 33, 1L << 34, 1L << 35, 1L << 36, 1L << 37, 1L << 38, 1L << 39,
        1L << 40, 1L << 41, 1L << 42, 1L << 43, 1L << 44, 1L << 45, 1L << 46, 1L << 47,
        1L << 48, 1L << 49, 1L << 50, 1L << 51, 1L << 52, 1L << 53, 1L << 54, 1L << 55,
        1L << 56, 1L << 57, 1L << 58, 1L << 59, 1L << 60, 1L << 61, 1L << 62, 1L << 63,
    ]

    def __init__(self, bit_length=10000, max_increment_size=10000):
        self._initializer = [BitMap.BASE_ITEM_VALUE]*((bit_length >> BitMap.OS_BIT_SHIFT) + 1)
        self._base = array.array(BitMap.BASE_ITEM_TYPE, self._initializer)
        self._base_bit_size = self._get_base_bit_size()
        self._max_increment_size = max_increment_size

    def _get_base_bit_size(self):
        return self._base.buffer_info()[1] << BitMap.OS_BIT_SHIFT

    def _extend(self):
        """Extend bitmap size dynamically"""
        if len(self._initializer) < self._max_increment_size:
            self._initializer = self._initializer * 2 # double the size
        tmp = array.array(BitMap.BASE_ITEM_TYPE, self._initializer)
        self._base.extend(tmp)
        self._base_bit_size = self._get_base_bit_size()

    def _is_exist(self, bit_loc):
        return bit_loc <= self._base_bit_size

    def _prepare(self, bit_loc):
        while not self._is_exist(bit_loc):
            self._extend()

    def _get_oprands(self, bit_loc, do_prepare=True):
        """uniforms the oprands for all upper callers for consistence.
        """
        if do_prepare: self._prepare(bit_loc)
        return bit_loc >> BitMap.OS_BIT_SHIFT , BitMap.BITS[bit_loc & BitMap.OS_BIT_MASK]

    def turnOn(self, bit_loc):
        idx, bit = self._get_oprands(bit_loc)
        self._base[idx] |= bit
        return self

    def turnOff(self, bit_loc):
        idx, bit = self._get_oprands(bit_loc)
        self._base[idx] &= ~bit
        return self

    def isTurnedOn(self, bit_loc):
        if bit_loc >= self._base_bit_size:
            return False
        idx, bit = self._get_oprands(bit_loc, do_prepare=False)
        return self._base[idx] & bit > 0

    def clearAll(self):
        base_len = self._base.buffer_info()[1]
        i = 0
        while i < base_len:
            self._base[i] = 0
            i += 1

    def erase(self):
        del self._base
        self._base_bit_size = 0

    def bitLength(self):
        return self._base_bit_size

    def info(self):
        """Return item type and item size in byte"""
        return dict(
            base_item_type      = BitMap.BASE_ITEM_TYPE,
            base_item_byte_size = BitMap.BASE_ITEM_BYTE_SIZE,
            base_item_bit_size  = BitMap.BASE_ITEM_BIT_SIZE,
            os_bit_shift        = BitMap.OS_BIT_SHIFT,
            os_bit_mask         = BitMap.OS_BIT_MASK,
            bit_length          = self.bitLength(),
            mem_size_in_kb      = self.bitLength() >> 13,
        )

    def negate(self):
        base_len = self._base.buffer_info()[1]
        i = 0
        while i < base_len:
            self._base[i] = ~self._base[i]
            i += 1
        # finally
        return self

    def union(self, bit_map):
        """ get shared part of self._base and @bit_map,
            store it into self._base
        """
        bm_left = self._base
        bm_right = bit_map
        bm_left_len = len(bm_left)
        bm_right_len = len(bm_right)

        bm_len = min(bm_left_len, bm_right_len)
        i = 0
        while i < bm_len:
            bm_left[i] |= bm_right[i]
            i += 1
        # extend bm_left (which is self._base) with extra data
        # of bm_right (the given argument) if exists.
        if bm_right_len > bm_len:
            extra_array = bm_right[bm_len:]
            bm_left.extend(extra_array)

        # finally
        return self

    def intersect(self, bit_map):
        """ get shared part of self._base and @bit_map,
            store it into self._base
        """
        bm_left = self._base
        bm_right = bit_map
        bm_left_len = len(bm_left)
        bm_right_len = len(bm_right)

        bm_len = min(bm_left_len, bm_right_len)
        i = 0
        while i < bm_len:
            bm_left[i] &= bm_right[i]
            i += 1
        # ignore extra array.

        # finally
        return self

    def reset(self):
        self._base = array.array(BitMap.BASE_ITEM_TYPE, [])

