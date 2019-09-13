<?xml version="1.0" encoding="UTF-8"?>
<!--
	XSLT Build-AllSchema-XSLT1:
	Builds the "All Schema" for the G2 Standards
	Copyright 2011, IPTC - International Press Telecommunications Council, www.iptc.org
	History:
	2011-02-21 v1 (Michael Steidl): initial version
--> 
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:iptc-ms="http://iptc.org/std/mergeschemas/">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<xsl:copy xml:space="default"><xsl:apply-templates select="*|@*|comment()|processing-instruction()|text()" /></xsl:copy>
	</xsl:template>
	 <!-- 
        Identity transform matches all nodes and passes them through unaltered. The priority is lower
        to ensure that other templates have a chance to act before this one.
    -->    
    <xsl:template match="*|@*|comment()|processing-instruction()|text()" priority="-1">
		<xsl:copy><xsl:apply-templates select="*|@*|comment()|processing-instruction()|text()" /></xsl:copy>
	</xsl:template>
	<!-- Filter out the annotations -->
	<xsl:template match="xs:annotation">
		<xsl:choose>
		<xsl:when test="xs:appinfo/iptc-ms:merge/@fname != '' ">
			<xsl:apply-templates select="xs:appinfo/iptc-ms:merge" />
		</xsl:when>
		<xsl:otherwise>
			<xsl:copy-of select="."/>
		</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!--Process the Merge Schema element-->
	<xsl:template match="xs:appinfo/iptc-ms:merge">
		<xsl:variable name="extschema" select="document(@fname)"/>
		<xsl:apply-templates select="$extschema/xs:schema" mode="inmerge"></xsl:apply-templates>
	</xsl:template>
	<!--Special procedure for merging in an XML Schema: only specific XML Schema elements should be merged-->
	<xsl:template match="xs:schema" mode="inmerge">
		<xsl:for-each select="xs:element">
			<xsl:copy-of select="."></xsl:copy-of>
		</xsl:for-each>
		<xsl:for-each select="xs:complexType">
			<xsl:copy-of select="."></xsl:copy-of>
		</xsl:for-each>
		<xsl:for-each select="xs:attributeGroup">
			<xsl:copy-of select="."></xsl:copy-of>
		</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>
