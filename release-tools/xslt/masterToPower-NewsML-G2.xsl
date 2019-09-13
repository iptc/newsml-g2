<?xml version="1.0" encoding="UTF-8"?>
<!-- 
	IPTC SCHEMA GENERATOR

	Created for the IPTC by Jay Cousins, RivCom Ltd (jay.cousins@rivcom.com) and Ulf Wingstedt, CNet Svenska AB (ulf.wingstedt@cnet.se)
	Date: 2006-12-29

    Convert IPTC schema from the master schema to the "power" profile.  

	CHANGE LOG
	Date: 2006-12-29
		Added iptc-x:powerFixed attribute.
	v 1.3: iptc-x:eventsml attribute added

-->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:iptc-x="http://iptc.org/std/nar/schemaextensions/"
    version="1.0" 
    exclude-result-prefixes="iptc-x">
    
    <xsl:output method="xml" encoding="UTF-8" version="1.0"/>

	<!-- Add a comment with the current version of the schema generator used to the output schema. -->
    <xsl:template match="/" >
        <xsl:copy><xsl:apply-templates select="*|@*|comment()|processing-instruction()|text()" /></xsl:copy>
       	<xsl:comment>IPTC Schema Generator, v 1.3</xsl:comment>
	</xsl:template>
    
    <!-- Change include file from the master to the power framework schema. 	-->
	<xsl:template match="xs:include[contains(@schemaLocation,'-spec-Framework-')]">
		<xsl:variable name="begin" select="substring-before(@schemaLocation, 'Master')"/>
 		<xsl:variable name="end" select="substring-after(@schemaLocation, 'Master')"/>
       <xs:include schemaLocation="{concat($begin,'Power', $end)}"/>
    </xsl:template>    

	<!-- Remove xml:space. -->
    <xsl:template match="@xml:space"/>
    
	<!-- Remove all iptc schema extensions from the target file -->
	<xsl:template match="@iptc-x:*"/>

	<!-- Remove all structures belonging to other profiles -->
	<xsl:template match="*[@iptc-x:profile = 'master']"/>
	<xsl:template match="*[@iptc-x:profile = 'core']"/>

	<!-- Remove all structures specific to EventsML-G2 -->
	<xsl:template match="*[@iptc-x:eventsml='true']"/>

	<!-- Handle profile specific comments -->
	<xsl:template match="xs:annotation[@iptc-x:profile = 'power']">
		<xsl:apply-templates select="xs:documentation/comment()"/>
	</xsl:template>

    <!-- 
        Find "iptc-x:powerMinOccurs" and "iptc-x:powerMaxOccurs" attributes in the schema and convert them to "xs:minOccurs" attributes 
        so they will be used. 
    -->
    <xsl:template match="@iptc-x:powerMinOccurs">
		<xsl:attribute name="minOccurs"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>
    <xsl:template match="@iptc-x:powerMaxOccurs">
		<xsl:attribute name="maxOccurs"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>


    <!-- 
        Find "iptc-x:powerUse"attributes in the schema and convert them to "use" attributes 
        so they will be used. 
    -->
    <xsl:template match="@iptc-x:powerUse">
		<xsl:attribute name="use"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>

    <!-- 
        Find "iptc-x:powerFixed"attributes in the schema and convert them to "fixed" attributes 
        so they will be used. 
    -->
    <xsl:template match="@iptc-x:powerFixed">
		<xsl:attribute name="fixed"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>

    <!-- 
        Find "iptc-x:power"attributes in the schema and convert them to "xs:type" attributes 
        so they will be used. 
    -->
    <xsl:template match="@iptc-x:power">
		<xsl:attribute name="type"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>

    <xsl:template match="xs:extension/@iptc-x:power" priority="1">
		<xsl:attribute name="base"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>

    <!-- Ditto for xs:restriction -->
    
    <xsl:template match="xs:restriction/@iptc-x:power" priority="1">
		<xsl:attribute name="base"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>    
    
    <!-- 
		Similarly to the previous two sets of templates, but when attached to an xs:group,
		the power attributes should go to the @ref attribute.
	-->
	
    <xsl:template match="xs:group/@iptc-x:power" priority="1">
		<xsl:attribute name="ref"><xsl:value-of select="."/></xsl:attribute>
	</xsl:template>        
    
    <!-- 
        Identity transform matches all nodes and passes them through unaltered. The priority is lower
        to ensure that other templates have a chance to act before this one.
    -->
    
    <xsl:template match="*|@*|comment()|processing-instruction()|text()" priority="-1">
		<xsl:copy><xsl:apply-templates select="*|@*|comment()|processing-instruction()|text()" /></xsl:copy>
	</xsl:template>
</xsl:stylesheet>
