async def get_today_report(zip_code=None, fishing_type=None):
    logger.info(f"Requesting today's report - location: {zip_code}, type: {fishing_type}")
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, get_fishing_report, zip_code, fishing_type)
        logger.info("Today's report completed")
        return result
    except Exception as e:
        logger.error(f"Today's report failed: {str(e)}")
        return f"❌ Error: {str(e)}"

async def get_tomorrow_report(zip_code=None, fishing_type=None):
    from datetime import timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    start = f"{tomorrow_str} 00:00"
    end = f"{tomorrow_str} 23:59"
    logger.info(f"Requesting tomorrow's report - location: {zip_code}, type: {fishing_type}")
    return await get_time_window_report(start, end, zip_code, fishing_type)

async def today_logic(interaction, zip_code, fishing_type, logger):
    user_id = interaction.user.id
    username = interaction.user.name
    logger.info(f"Command /fish today - User: {username} (ID: {user_id}), zip_code: {zip_code}, type: {fishing_type}")
 
    if not zip_code:
        logger.warning(f"User {username} attempted /fish today without location")
        await interaction.response.send_message("❌ Please set your ZIP code first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    try:
        report = await get_today_report(zip_code, fishing_type)
        if len(report) > 2000:
            logger.warning(f"Report truncated for user {username} (length: {len(report)})")
            report = report[:1950] + "\n\n... (truncated)"
        await interaction.followup.send(report)
        logger.info(f"Successfully sent today's report to {username}")
    except Exception as e:
        logger.error(f"Failed to send report to {username}: {str(e)}")
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

async def tomorrow_logic(interaction, zip_code, fishing_type, logger):
    user_id = interaction.user.id
    username = interaction.user.name
    logger.info(f"Command /fish tomorrow - User: {username} (ID: {user_id}), zip_code: {zip_code}, type: {fishing_type}")
     
    if not zip_code:
        logger.warning(f"User {username} attempted /fish tomorrow without location")
        await interaction.response.send_message("❌ Please set your ZIP code first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    try:
        report = await get_tomorrow_report(zip_code, fishing_type)
        if len(report) > 2000:
            logger.warning(f"Report truncated for user {username} (length: {len(report)})")
            report = report[:1950] + "\n\n... (truncated)"
        await interaction.followup.send(report)
        logger.info(f"Successfully sent tomorrow's report to {username}")
    except Exception as e:
        logger.error(f"Failed to send report to {username}: {str(e)}")
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
