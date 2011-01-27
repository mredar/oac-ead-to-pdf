<!-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ -->
<!-- scale images; max dim or max x and max y                               -->
<!--                                                  -->
<!-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ -->

<!--
   Copyright (c) 2006, Regents of the University of California
   All rights reserved.
 
   Redistribution and use in source and binary forms, with or without 
   modification, are permitted provided that the following conditions are 
   met:

   - Redistributions of source code must retain the above copyright notice, 
     this list of conditions and the following disclaimer.
   - Redistributions in binary form must reproduce the above copyright 
     notice, this list of conditions and the following disclaimer in the 
     documentation and/or other materials provided with the distribution.
   - Neither the name of the University of California nor the names of its
     contributors may be used to endorse or promote products derived from 
     this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
   POSSIBILITY OF SUCH DAMAGE.
-->

<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="scale-max">
  <xsl:param name="max"/>
  <xsl:param name="x"/>
  <xsl:param name="y"/>
  <xsl:call-template name="scale-maxXY">
    <xsl:with-param name="maxX" select="number($max)"/>
    <xsl:with-param name="maxY" select="number($max)"/>
    <xsl:with-param name="x" select="number($x)"/>
    <xsl:with-param name="y" select="number($y)"/>
  </xsl:call-template>
</xsl:template>


<xsl:template name="scale-maxXY">
  <xsl:param name="maxX"/>
  <xsl:param name="maxY"/>
  <xsl:param name="x"/>
  <xsl:param name="y"/>
  <xsl:variable name="ratio" select="number($x) div number($y)"/>
  <xsl:variable name="maxRatio" select="number($maxX) div number($maxY)"/>
  <xsl:variable name="width">
   <xsl:choose>
        <xsl:when test="$x &gt; number($maxX) or $y &gt; number($maxY)">
           <xsl:choose>
                <xsl:when test="$ratio &gt; $maxRatio"><!-- landscape, x leads -->
                        <xsl:value-of select="number($maxX)"/>
                </xsl:when>
                <xsl:when test="$ratio &lt; $maxRatio"><!-- portrait, y leads; x is scaled -->
                       <xsl:value-of select="round(number($maxY) * $ratio)"/>
                </xsl:when>
                <xsl:when test="$ratio =  $maxRatio"><!-- what a square! -->
                        <xsl:value-of select="number($maxX)"/>
                </xsl:when>
           </xsl:choose>
        </xsl:when>
        <xsl:when test="$x"><xsl:value-of select="$x"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="$maxX"/></xsl:otherwise>
   </xsl:choose>
  </xsl:variable>
  <xsl:variable name="height">
   <xsl:choose>
        <xsl:when test="$x &gt; number($maxX) or $y &gt; number($maxY)">
           <xsl:choose>
                <xsl:when test="$ratio &gt; $maxRatio"><!-- landscape, x leads; y is scaled -->
                        <xsl:value-of select="round(number($maxX) div $ratio)"/>
                </xsl:when>
                <xsl:when test="$ratio &lt; $maxRatio"><!-- portrait, y leads -->
                        <xsl:value-of select="number($maxY)"/>
                </xsl:when>
                <xsl:when test="$ratio =  $maxRatio"><!-- what a square! -->
                        <xsl:value-of select="number($maxX)"/>
                </xsl:when>
           </xsl:choose>
        </xsl:when>
        <xsl:when test="$y"><xsl:value-of select="$y"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="$maxY"/></xsl:otherwise>
   </xsl:choose>
  </xsl:variable>
	
  <xy width="{$width}" height="{$height}"/>

</xsl:template>
 
</xsl:stylesheet> 
