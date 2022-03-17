# @author: Ericsson Colborn, NYU '23 Computer & Data Science
# Database Management
# Professor Versoza
# New York University

# Part 1 of Homework #01

'''
BitList class: creates a new series of bits from a string that represents
a binary number

Requirements:
    string should only consist of 0's and 1's
        - if it doesnt, raise ValueError with an appropriate message
        - if it's valid, save the bits on self (probably as str)
'''
 

# BitList class
class BitList:
    
    # initializes BitList with the passed string of bits as the attribute 'bits'
    def __init__(self, bits):
        if len(bits) == 0:
            raise ValueError("BitList must be non-empty")
        for b in bits:
            if b not in ['0', '1']:
                raise ValueError("BitList can only contain 0's and 1's")
        self.bits = bits
        
    # determines equality by comparing each BitList's 'bits' attribute
    def __eq__(self, other):
        if self.bits == other.bits:
            return True
        else:
            return False
    
    # Static method, converts a variable number of 0's and 1's into a new BitList
    @staticmethod
    def from_ints(*bits):

        # check that every arg is 0 or 1
        for bit in bits:
            if bit not in [0, 1]:
                raise ValueError("BitList can only contain 0's and 1's")

        # if it passes the check, create a str from the bits...
        new_bits = ''.join([str(bit) for bit in bits])
        # and make a new BitList with it
        return BitList(new_bits)
            
    # for print()
    def __str__(self):
        return(self.bits)
    
    # arithmetic shift left and right (basically just str manipulation)
    def arithmetic_shift_left(self):
        self.bits = self.bits[1:len(self.bits)]
        self.bits = self.bits + "0"
        
    def arithmetic_shift_right(self):
        self.bits = self.bits[0:len(self.bits)-1]
        self.bits = self.bits[0] + self.bits
    
    # bitwise and:
    def bitwise_and(self, otherBitList):

        # first, confirm that otherBitList is in fact a BitList:
        if type(otherBitList) != BitList:
            raise ValueError("Both BitLists must be of type BitList.")

        # first check that the lengths of each BitList are equal:
        if len(self.bits) != len(otherBitList.bits):
            raise ValueError("BitLists must be the same length to perform bitwise 'AND'")

        # convert each BL to ints so their contents can be multiplied
        bitList_asInt = [int(bit) for bit in self.bits]
        bitList2_asInt = [int(bit) for bit in otherBitList.bits]
        
        temp = [bitList_asInt[i] * bitList2_asInt[i]
                              for i in range(len(bitList_asInt))]
        
        # convert the product back to a string
        temp = ''.join([str(b) for b in temp])
        return BitList(temp)

    # helper function for chunk
    def toList(self):
        return [int(bit) for bit in self.bits]

    # chunk:
    def chunk(self, chunk_length):

        # make sure the BL can be split into equal chunks of chunk_length
        if len(self.bits) % chunk_length != 0:
            raise ChunkError(f"Cannot split bits into chunk of length {chunk_length}")
        
        chunk_list = []
        start = 0

        # for however many chunks there's going to be...
        for i in range(0, len(self.bits) // chunk_length):

            # append the chunk to the list of chunks...
            chunk_list.append(self.toList()[start:start+chunk_length])

            # increment starting pos so it's set up for the next chunk
            start = start + chunk_length

        return chunk_list
    
    # decode! this one was fun :')
    def decode(self, encoding='utf-8'):

        # first check that a valid encoding was passed
        if encoding not in ['us-ascii', 'utf-8']:
            raise ValueError("Only us-ascii and utf-8 encodings are supported")
        
        # handle ascii first (since it's easier):
        if encoding == 'us-ascii':

            # initialize a string to be returned
            return_str = ''
            
            try:
                # try to split into 7-bit chunks
                chunks = self.chunk(7)
                
            except ChunkError:
                
                try:
                    # if that fails, try 8
                    chunks = self.chunk(8)

                except ChunkError: 
                    # if that doesn't work, nothing will... ret an error msg
                    return "Invald bit length for ASCII encoding"
                
            # once we got the chunks...
            for chunk in chunks:

                temp = "".join([str(c) for c in chunk])

                try:
                    # try to convert to using chr()
                    return_str = return_str + chr(int(temp, 2))
   
                except:
                    print("Bit value too large to decode with ascii")
            
            return return_str
      
        # if encoding = utf-8 (or no val was passed)...
        if encoding == 'utf-8':
            
            num_bytes = 0
            
            # if the leading bit is 0, then we just need 1 byte
            if self.bits[0] == '0':
                num_bytes = 1

            # else, count the number of leading 1's
            else:
                i = 0
                while len(self.bits) > i and self.bits[i] == '1':
                    num_bytes += 1
                    i = i+1

                # if there's a single leading 1, that is invalid:
                if num_bytes == 1:
                        raise DecodeError("Invalid leading byte (1xxx)") 

            # if the input str contains separate characters,
            # we need to split them up
            chrs = []
            chrs.append(self.bits[:num_bytes*8])
            current_chr = self.bits[num_bytes*8:]
           
           # aka 'while there's more than 1 chr left'
            while len(current_chr) >= 8:
                
                # repeat the process
                num_bytes = 0
                if current_chr[0] == '0':
                    num_bytes = 1
                    
                else:
                    i = 0
                    while current_chr[i] == '1':
                        num_bytes += 1
                        i += 1

                    if num_bytes == 1:
                        raise DecodeError("Invalid leading byte (1xxx)") 
                        
                chrs.append(current_chr[:num_bytes*8])
                current_chr = current_chr[num_bytes*8:]

            # same deal with the string to be returned
            return_str = ''

            # once we've split into chars...
            for c in chrs:
                
                tempBL = BitList(c)
    
                try:
                    # see if the leading byte of each is valid
                    num_bytes = len(tempBL.chunk(8))

                except ChunkError:
                    raise DecodeError("Invalid leading byte")

                # attack each byte of each chr one-by-one
                actual_val = tempBL.bits[num_bytes:8]
                start = 8

                for i in range(2, num_bytes+1):
                        
                    if c[start:8*i][:2] == '10':
            
                        # scrape off the bits that are meaningful
                        actual_val += c[start+2:8*i]
                        # and move the start index to the next byte
                        start += 8

                    else:
                        raise DecodeError("Invalid continuation byte")
          
                return_str += chr(int(actual_val, 2))
            
            return return_str

# custom errors:
class DecodeError(Exception):
    pass
                
class ChunkError(Exception):
    pass