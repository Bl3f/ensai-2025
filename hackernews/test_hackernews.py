def test_extract_news():
    from main import extract_one_link
    date = '2025-02-20'
    html = """
    <tr class='athing submission' id='43089238'>
       <td align="right" valign="top" class="title">
          <span class="rank">30.</span>
       </td>
       <td valign="top" class="votelinks">
          <center>
             <a id='up_43089238' href='vote?id=43089238&amp;how=up&amp;goto=front%3Fday%3D2025-02-20'>
                <div class='votearrow' title='upvote'></div>
             </a>
          </center>
       </td>
       <td class="title">
          <span class="titleline">
          <a href="https://httl.dev/docs/cli">Show HN: A Fast HTTP Request CLI Powered by HTTL</a>
          <span class="sitebit comhead"> (<a href="from?site=httl.dev"><span class="sitestr">httl.dev</span></a>)</span></span>
       </td>
    </tr>
    <tr>
       <td colspan="2"></td>
       <td class="subtext"><span class="subline">
          <span class="score" id="score_43089238">51 points</span> by <a href="user?id=emykhailenko" class="hnuser">emykhailenko</a> <span class="age" title="2025-02-18T13:31:49 1739885509"><a href="item?id=43089238">5 days ago</a></span> <span id="unv_43089238"></span> | <a href="item?id=43089238">16&nbsp;comments</a>        </span>
       </td>
    </tr>
    """
    assert extract_one_link(html, date) == {
        'rank': 30,
        'title': 'Show HN: A Fast HTTP Request CLI Powered by HTTL',
        'url': 'https://httl.dev/docs/cli',
        'author': 'emykhailenko',
        'points': 51,
        'comments': 16,
        'created_at': '2025-02-18T13:31:49 1739885509',
        'partition_date': date,
    }
